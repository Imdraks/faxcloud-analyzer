"""
Moteur Asterisk pour FaxCloud Analyzer
=======================================
Ce module permet de classifier les numéros de fax en :
  - SDA Fax : numéro qui répond avec une tonalité fax (CNG 1100Hz / CED 2100Hz)
  - Téléphone : numéro qui répond avec une voix ou tonalité classique

Trois méthodes de détection (par priorité) :
  1. Cache local : résultat d'un appel test précédent (BDD)
  2. Appel test via Asterisk AMI : Originate + AMD/FaxDetect
  3. Classification par préfixe : fallback si pas d'Asterisk

Architecture :
  AsteriskEngine
    ├── Cache BDD (tone_detection_cache)
    ├── AMI : Originate → AMD() + FaxDetect
    ├── Plages SDA manuelles (fallback)
    └── Classification préfixe FR (fallback)

Tonalités fax :
  - CNG (Calling Tone)  : 1100 Hz, émis par l'appelant fax
  - CED (Called Station) : 2100 Hz, émis par le récepteur fax
  - Si l'une des deux est détectée → c'est un fax
"""

from __future__ import annotations

import json
import logging
import re
import socket
import sqlite3
import time
import uuid
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple

from .config import settings, ensure_directories

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# Types de numéros
# ──────────────────────────────────────────────

NUMBER_TYPE_SDA_FAX = "sda_fax"
NUMBER_TYPE_SDA = "sda"
NUMBER_TYPE_PHONE = "phone"
NUMBER_TYPE_GEOGRAPHIC = "geographic"
NUMBER_TYPE_MOBILE = "mobile"
NUMBER_TYPE_SPECIAL = "special"
NUMBER_TYPE_SHORT = "short"
NUMBER_TYPE_INTERNATIONAL = "international"
NUMBER_TYPE_UNKNOWN = "unknown"
NUMBER_TYPE_NO_ANSWER = "no_answer"
NUMBER_TYPE_BUSY = "busy"
NUMBER_TYPE_ERROR = "error"

# Labels français
NUMBER_TYPE_LABELS = {
    NUMBER_TYPE_SDA_FAX: "SDA Fax (tonalité détectée)",
    NUMBER_TYPE_SDA: "SDA (Interne PBX)",
    NUMBER_TYPE_PHONE: "Téléphone (voix)",
    NUMBER_TYPE_GEOGRAPHIC: "Téléphone fixe",
    NUMBER_TYPE_MOBILE: "Téléphone mobile",
    NUMBER_TYPE_SPECIAL: "Numéro spécial",
    NUMBER_TYPE_SHORT: "Numéro court",
    NUMBER_TYPE_INTERNATIONAL: "International",
    NUMBER_TYPE_UNKNOWN: "Inconnu",
    NUMBER_TYPE_NO_ANSWER: "Pas de réponse",
    NUMBER_TYPE_BUSY: "Occupé",
    NUMBER_TYPE_ERROR: "Erreur d'appel",
}

# Résultats de détection de tonalité
TONE_FAX = "fax"
TONE_VOICE = "voice"
TONE_NO_ANSWER = "no_answer"
TONE_BUSY = "busy"
TONE_ERROR = "error"
TONE_UNKNOWN = "unknown"


# ──────────────────────────────────────────────
# Configuration AMI
# ──────────────────────────────────────────────

@dataclass
class AMIConfig:
    """Configuration de connexion Asterisk Manager Interface."""
    host: str = "127.0.0.1"
    port: int = 5038
    username: str = "admin"
    secret: str = ""
    enabled: bool = False
    context: str = "faxcloud-detect"   # Contexte dialplan pour détection fax
    caller_id: str = "FaxCloudTest"    # CallerID pour les appels test
    call_timeout: int = 15             # Timeout appel test (secondes)
    detect_timeout: int = 10           # Temps d'écoute de la tonalité après décrochage
    trunk: str = ""                    # Trunk SIP à utiliser (ex: "PJSIP/trunk-orange")
    cache_ttl_hours: int = 24 * 7     # Durée de validité du cache (7 jours)


@dataclass
class SDARange:
    """Plage de numéros SDA."""
    id: str = ""
    label: str = ""
    prefix: str = ""          # Ex: "33493" pour les numéros CHU Nice
    range_start: str = ""     # Ex: "0000"
    range_end: str = ""       # Ex: "9999"
    site: str = ""            # Ex: "CHU Nice"
    description: str = ""


# ──────────────────────────────────────────────
# Connexion AMI
# ──────────────────────────────────────────────

class AMIConnection:
    """
    Client AMI (Asterisk Manager Interface) avec détection de tonalité fax.
    
    Fonctionnement de la détection :
      1. Originate un appel vers le numéro cible
      2. L'appel entre dans le contexte 'faxcloud-detect' du dialplan
      3. Le dialplan exécute AMD() puis Wait — Asterisk analyse la tonalité
      4. On écoute les événements AMI :
         - ChannelVarSet AMDSTATUS=MACHINE + AMDCAUSE=TONEFAX → fax détecté
         - ChannelVarSet FAXDETECTED=1 → fax détecté (via FaxDetect)
         - Hangup avec cause 17 → occupé
         - Hangup avec cause 19/21 → pas de réponse
         - ChannelVarSet AMDSTATUS=HUMAN → voix humaine
      5. On raccroche et on retourne le résultat
    """

    def __init__(self, config: AMIConfig):
        self.config = config
        self._socket: Optional[socket.socket] = None
        self._connected = False
        self._action_counter = 0

    def connect(self) -> bool:
        if not self.config.enabled:
            logger.info("AMI désactivé dans la configuration")
            return False
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.settimeout(5)
            self._socket.connect((self.config.host, self.config.port))

            banner = self._recv()
            if "Asterisk" not in banner:
                logger.warning("Réponse inattendue du serveur AMI: %s", banner)
                self.disconnect()
                return False

            self._send(
                f"Action: Login\r\n"
                f"Username: {self.config.username}\r\n"
                f"Secret: {self.config.secret}\r\n"
                f"\r\n"
            )
            response = self._recv()
            if "Success" in response:
                self._connected = True
                logger.info("Connecté à Asterisk AMI %s:%s", self.config.host, self.config.port)
                return True
            else:
                logger.error("Échec auth AMI: %s", response.strip())
                self.disconnect()
                return False
        except (socket.error, OSError) as e:
            logger.error("Connexion AMI impossible: %s", e)
            self.disconnect()
            return False

    def disconnect(self) -> None:
        if self._socket:
            try:
                if self._connected:
                    self._send("Action: Logoff\r\n\r\n")
                self._socket.close()
            except (socket.error, OSError):
                pass
            finally:
                self._socket = None
                self._connected = False

    def _next_action_id(self) -> str:
        self._action_counter += 1
        return f"faxcloud-{self._action_counter}-{uuid.uuid4().hex[:8]}"

    def _send(self, data: str) -> None:
        if self._socket:
            self._socket.sendall(data.encode("utf-8"))

    def _recv(self, bufsize: int = 4096) -> str:
        if self._socket:
            return self._socket.recv(bufsize).decode("utf-8", errors="replace")
        return ""

    def _recv_all(self, timeout: float = 3.0) -> str:
        if not self._socket:
            return ""
        self._socket.settimeout(timeout)
        chunks = []
        try:
            while True:
                chunk = self._socket.recv(8192).decode("utf-8", errors="replace")
                if not chunk:
                    break
                chunks.append(chunk)
                if "EventList: Complete" in chunk or "Response: Goodbye" in chunk:
                    break
        except socket.timeout:
            pass
        return "".join(chunks)

    def _read_events(self, timeout: float, channel_filter: str = "") -> List[Dict]:
        """Lit les événements AMI pendant `timeout` secondes."""
        if not self._socket:
            return []
        
        events = []
        deadline = time.time() + timeout
        buffer = ""
        
        while time.time() < deadline:
            remaining = max(0.1, deadline - time.time())
            self._socket.settimeout(min(remaining, 1.0))
            try:
                chunk = self._socket.recv(8192).decode("utf-8", errors="replace")
                if not chunk:
                    break
                buffer += chunk
                
                # Parser les événements (séparés par \r\n\r\n)
                while "\r\n\r\n" in buffer:
                    event_str, buffer = buffer.split("\r\n\r\n", 1)
                    event = self._parse_event(event_str)
                    if event:
                        # Filtrer par channel/actionid si demandé
                        if channel_filter:
                            # Vérifier ActionID d'abord
                            aid = event.get("ActionID", "")
                            if aid == channel_filter:
                                pass  # Match par ActionID
                            else:
                                ch = event.get("Channel", event.get("channel", ""))
                                uid = event.get("Uniqueid", "")
                                if (channel_filter not in ch and ch not in channel_filter
                                        and channel_filter not in uid):
                                    continue
                        events.append(event)
                        
                        # Conditions d'arrêt anticipé
                        event_name = event.get("Event", "")
                        if event_name == "Hangup":
                            return events
                        
                        # Variable fax détectée
                        var_name = event.get("Variable", "")
                        if var_name in ("AMDSTATUS", "FAXDETECTED", "FAXDETECT"):
                            # Continuer un peu pour récupérer AMDCAUSE
                            deadline = min(deadline, time.time() + 2)
                            
            except socket.timeout:
                continue
            except (socket.error, OSError):
                break
        
        return events

    @staticmethod
    def _parse_event(raw: str) -> Optional[Dict]:
        event = {}
        for line in raw.split("\r\n"):
            line = line.strip()
            if not line:
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                event[key.strip()] = val.strip()
        return event if event else None

    def detect_fax_tone(self, numero: str) -> Dict:
        """
        Appelle un numéro et détecte si c'est un fax via la tonalité.
        
        Retourne:
          {
            "numero": "33493095562",
            "tone": "fax" | "voice" | "no_answer" | "busy" | "error",
            "is_fax": True/False,
            "details": "CNG tone detected" | "Human voice" | ...,
            "duration_ms": 3200,
            "hangup_cause": 16,
            "raw_events": [...]
          }
        """
        if not self._connected:
            return self._error_result(numero, "AMI non connecté")

        action_id = self._next_action_id()
        
        # Construire le numéro à appeler
        # Si un trunk est configuré, l'utiliser. Sinon, passer par le contexte.
        if self.config.trunk:
            channel = f"{self.config.trunk}/{numero}"
        else:
            channel = f"Local/{numero}@{self.config.context}"

        logger.info("Détection fax: appel de %s (ActionID: %s)", numero, action_id)
        start_time = time.time()

        # Originate : appeler le numéro et le connecter au contexte de détection
        # L'extension 'detect' dans le contexte faxcloud-detect exécutera AMD()
        self._send(
            f"Action: Originate\r\n"
            f"ActionID: {action_id}\r\n"
            f"Channel: {channel}\r\n"
            f"Context: {self.config.context}\r\n"
            f"Exten: detect\r\n"
            f"Priority: 1\r\n"
            f"CallerID: {self.config.caller_id}\r\n"
            f"Timeout: {self.config.call_timeout * 1000}\r\n"
            f"Async: true\r\n"
            f"Variable: FAXCLOUD_TEST=1\r\n"
            f"\r\n"
        )

        # Lire la réponse initiale de l'Originate
        initial = self._recv()
        if "Error" in initial:
            error_msg = "Originate refusé"
            for line in initial.split("\r\n"):
                if line.startswith("Message:"):
                    error_msg = line.split(":", 1)[1].strip()
            return self._error_result(numero, error_msg)

        # Écouter les événements pendant la durée de l'appel + détection
        total_timeout = self.config.call_timeout + self.config.detect_timeout + 5
        events = self._read_events(total_timeout, channel_filter=action_id)

        duration_ms = int((time.time() - start_time) * 1000)

        # Analyser les événements pour déterminer le résultat
        return self._analyze_events(numero, events, duration_ms)

    def _analyze_events(self, numero: str, events: List[Dict], duration_ms: int) -> Dict:
        """Analyse les événements AMI pour déterminer si c'est un fax."""
        
        tone = TONE_UNKNOWN
        details = ""
        hangup_cause = 0
        amd_status = ""
        amd_cause = ""
        fax_detected = False

        for event in events:
            event_name = event.get("Event", "")
            
            # Détection AMD
            if event_name == "ChannelVarSet" or event_name == "VarSet":
                var_name = event.get("Variable", "")
                var_value = event.get("Value", "")
                
                if var_name == "AMDSTATUS":
                    amd_status = var_value
                elif var_name == "AMDCAUSE":
                    amd_cause = var_value
                elif var_name in ("FAXDETECTED", "FAXDETECT"):
                    if var_value in ("1", "yes", "true", "fax"):
                        fax_detected = True
                elif var_name == "FAXMODE":
                    if var_value in ("detect", "gateway"):
                        fax_detected = True

            # Événement de détection fax spécifique
            if event_name in ("FAXStatus", "ReceiveFAXStatus", "SendFAXStatus"):
                fax_detected = True

            # Hangup
            if event_name == "Hangup":
                cause = event.get("Cause", "0")
                try:
                    hangup_cause = int(cause)
                except (ValueError, TypeError):
                    hangup_cause = 0

        # Déterminer le résultat final
        if fax_detected:
            tone = TONE_FAX
            details = "Tonalité fax détectée (CNG/CED)"
        elif amd_status.upper() == "MACHINE" and "FAX" in amd_cause.upper():
            tone = TONE_FAX
            details = f"AMD: tonalité fax ({amd_cause})"
        elif amd_status.upper() == "MACHINE":
            # Machine mais pas fax = répondeur
            tone = TONE_VOICE
            details = f"Répondeur détecté ({amd_cause})"
        elif amd_status.upper() == "HUMAN":
            tone = TONE_VOICE
            details = "Voix humaine détectée"
        elif amd_status.upper() == "NOTSURE":
            tone = TONE_UNKNOWN
            details = "Détection incertaine"
        elif hangup_cause == 17:
            tone = TONE_BUSY
            details = "Ligne occupée"
        elif hangup_cause in (19, 21, 18):
            tone = TONE_NO_ANSWER
            details = "Pas de réponse"
        elif hangup_cause == 1:
            tone = TONE_ERROR
            details = "Numéro non attribué"
        elif hangup_cause in (34, 38, 42, 44, 47):
            tone = TONE_ERROR
            details = f"Erreur réseau (cause {hangup_cause})"
        elif hangup_cause == 16:
            # Raccrochage normal sans détection = probablement voix
            if not amd_status:
                tone = TONE_UNKNOWN
                details = "Appel terminé sans détection"
            else:
                tone = TONE_VOICE
                details = "Raccrochage normal (voix probable)"
        elif not events:
            tone = TONE_ERROR
            details = "Aucun événement reçu"

        return {
            "numero": numero,
            "tone": tone,
            "is_fax": tone == TONE_FAX,
            "details": details,
            "duration_ms": duration_ms,
            "hangup_cause": hangup_cause,
            "amd_status": amd_status,
            "amd_cause": amd_cause,
            "raw_events_count": len(events),
        }

    @staticmethod
    def _error_result(numero: str, error: str) -> Dict:
        return {
            "numero": numero,
            "tone": TONE_ERROR,
            "is_fax": False,
            "details": error,
            "duration_ms": 0,
            "hangup_cause": 0,
            "amd_status": "",
            "amd_cause": "",
            "raw_events_count": 0,
        }

    def get_sip_peers(self) -> List[Dict]:
        if not self._connected:
            return []
        try:
            self._send("Action: SIPpeers\r\n\r\n")
            response = self._recv_all()
            return self._parse_list_response(response, "ObjectName")
        except (socket.error, OSError) as e:
            logger.error("Erreur AMI SIPpeers: %s", e)
            return []

    def get_pjsip_endpoints(self) -> List[Dict]:
        if not self._connected:
            return []
        try:
            self._send("Action: PJSIPShowEndpoints\r\n\r\n")
            response = self._recv_all()
            return self._parse_list_response(response, "ObjectName", "Endpoint")
        except (socket.error, OSError) as e:
            logger.error("Erreur AMI PJSIPShowEndpoints: %s", e)
            return []

    @staticmethod
    def _parse_list_response(response: str, *id_keys: str) -> List[Dict]:
        items = []
        current: Dict = {}
        for line in response.split("\r\n"):
            line = line.strip()
            if not line:
                if any(current.get(k) for k in id_keys):
                    items.append(current)
                current = {}
                continue
            if ":" in line:
                key, _, val = line.partition(":")
                current[key.strip()] = val.strip()
        return items


# ──────────────────────────────────────────────
# Base de données SDA
# ──────────────────────────────────────────────

def _connect_db() -> sqlite3.Connection:
    ensure_directories()
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_asterisk_tables() -> None:
    """Crée les tables pour la configuration Asterisk/SDA."""
    conn = _connect_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS asterisk_config (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            ami_host TEXT DEFAULT '127.0.0.1',
            ami_port INTEGER DEFAULT 5038,
            ami_username TEXT DEFAULT 'admin',
            ami_secret TEXT DEFAULT '',
            ami_enabled INTEGER DEFAULT 0,
            ami_context TEXT DEFAULT 'faxcloud-detect',
            ami_caller_id TEXT DEFAULT 'FaxCloudTest',
            ami_call_timeout INTEGER DEFAULT 15,
            ami_detect_timeout INTEGER DEFAULT 10,
            ami_trunk TEXT DEFAULT '',
            cache_ttl_hours INTEGER DEFAULT 168,
            updated_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS sda_ranges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            label TEXT NOT NULL,
            prefix TEXT NOT NULL,
            range_start TEXT DEFAULT '',
            range_end TEXT DEFAULT '',
            site TEXT DEFAULT '',
            description TEXT DEFAULT '',
            created_at TEXT,
            updated_at TEXT
        )
    """)

    # Cache des résultats de détection de tonalité
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tone_detection_cache (
            numero TEXT PRIMARY KEY,
            tone TEXT NOT NULL,
            is_fax INTEGER NOT NULL DEFAULT 0,
            details TEXT DEFAULT '',
            duration_ms INTEGER DEFAULT 0,
            hangup_cause INTEGER DEFAULT 0,
            amd_status TEXT DEFAULT '',
            amd_cause TEXT DEFAULT '',
            detected_at TEXT NOT NULL,
            expires_at TEXT NOT NULL
        )
    """)

    # Ajout de la colonne numero_type aux fax_entries (migration)
    for stmt in (
        "ALTER TABLE fax_entries ADD COLUMN numero_type TEXT DEFAULT 'unknown'",
        "ALTER TABLE fax_entries ADD COLUMN numero_type_label TEXT DEFAULT ''",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    # Migration: nouvelles colonnes asterisk_config
    for stmt in (
        "ALTER TABLE asterisk_config ADD COLUMN ami_context TEXT DEFAULT 'faxcloud-detect'",
        "ALTER TABLE asterisk_config ADD COLUMN ami_caller_id TEXT DEFAULT 'FaxCloudTest'",
        "ALTER TABLE asterisk_config ADD COLUMN ami_call_timeout INTEGER DEFAULT 15",
        "ALTER TABLE asterisk_config ADD COLUMN ami_detect_timeout INTEGER DEFAULT 10",
        "ALTER TABLE asterisk_config ADD COLUMN ami_trunk TEXT DEFAULT ''",
        "ALTER TABLE asterisk_config ADD COLUMN cache_ttl_hours INTEGER DEFAULT 168",
    ):
        try:
            cur.execute(stmt)
        except sqlite3.OperationalError:
            pass

    cur.execute("INSERT OR IGNORE INTO asterisk_config (id) VALUES (1)")
    conn.commit()
    conn.close()
    logger.info("Tables Asterisk initialisées")


# ──────────────────────────────────────────────
# CRUD Plages SDA
# ──────────────────────────────────────────────

def get_sda_ranges() -> List[Dict]:
    conn = _connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sda_ranges ORDER BY prefix, range_start")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def add_sda_range(label: str, prefix: str, range_start: str = "", range_end: str = "",
                  site: str = "", description: str = "") -> Dict:
    from datetime import datetime, timezone
    conn = _connect_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cur.execute(
        """
        INSERT INTO sda_ranges (label, prefix, range_start, range_end, site, description, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (label, prefix.strip(), range_start.strip(), range_end.strip(), site, description, now, now),
    )
    conn.commit()
    row_id = cur.lastrowid
    conn.close()
    logger.info("Plage SDA ajoutée: %s (prefix=%s)", label, prefix)
    return {"id": row_id, "label": label, "prefix": prefix, "range_start": range_start,
            "range_end": range_end, "site": site, "description": description}


def update_sda_range(range_id: int, **kwargs) -> bool:
    from datetime import datetime, timezone
    allowed = {"label", "prefix", "range_start", "range_end", "site", "description"}
    updates = {k: v for k, v in kwargs.items() if k in allowed}
    if not updates:
        return False
    updates["updated_at"] = datetime.now(timezone.utc).isoformat()
    set_clause = ", ".join(f"{k} = ?" for k in updates)
    values = list(updates.values()) + [range_id]
    conn = _connect_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE sda_ranges SET {set_clause} WHERE id = ?", values)
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


def delete_sda_range(range_id: int) -> bool:
    conn = _connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM sda_ranges WHERE id = ?", (range_id,))
    conn.commit()
    changed = cur.rowcount > 0
    conn.close()
    return changed


# ──────────────────────────────────────────────
# Configuration AMI (CRUD)
# ──────────────────────────────────────────────

def get_ami_config() -> Dict:
    conn = _connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM asterisk_config WHERE id = 1")
    row = cur.fetchone()
    conn.close()
    if row:
        config = dict(row)
        # Surcharge par variable d'environnement Docker (ASTERISK_HOST / ASTERISK_PORT)
        env_host = os.environ.get("ASTERISK_HOST")
        env_port = os.environ.get("ASTERISK_PORT")
        if env_host:
            config["ami_host"] = env_host
        if env_port:
            config["ami_port"] = int(env_port)
        return config
    return {"ami_host": os.environ.get("ASTERISK_HOST", "127.0.0.1"),
            "ami_port": int(os.environ.get("ASTERISK_PORT", "5038")),
            "ami_username": "admin",
            "ami_secret": "", "ami_enabled": 0, "ami_context": "faxcloud-detect",
            "ami_caller_id": "FaxCloudTest", "ami_call_timeout": 15,
            "ami_detect_timeout": 10, "ami_trunk": "", "cache_ttl_hours": 168}


def save_ami_config(host: str, port: int, username: str, secret: str, enabled: bool,
                    context: str = "faxcloud-detect", caller_id: str = "FaxCloudTest",
                    call_timeout: int = 15, detect_timeout: int = 10,
                    trunk: str = "", cache_ttl_hours: int = 168) -> None:
    conn = _connect_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cur.execute(
        """
        INSERT OR REPLACE INTO asterisk_config 
        (id, ami_host, ami_port, ami_username, ami_secret, ami_enabled,
         ami_context, ami_caller_id, ami_call_timeout, ami_detect_timeout,
         ami_trunk, cache_ttl_hours, updated_at)
        VALUES (1, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (host, port, username, secret, 1 if enabled else 0,
         context, caller_id, call_timeout, detect_timeout,
         trunk, cache_ttl_hours, now),
    )
    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
# Cache de détection de tonalité
# ──────────────────────────────────────────────

def get_cached_tone(numero: str) -> Optional[Dict]:
    """Retourne le résultat en cache si valide, sinon None."""
    conn = _connect_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc).isoformat()
    cur.execute(
        "SELECT * FROM tone_detection_cache WHERE numero = ? AND expires_at > ?",
        (numero, now),
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def save_tone_cache(result: Dict, ttl_hours: int = 168) -> None:
    """Sauvegarde un résultat de détection en cache."""
    conn = _connect_db()
    cur = conn.cursor()
    now = datetime.now(timezone.utc)
    expires = now + timedelta(hours=ttl_hours)
    cur.execute(
        """
        INSERT OR REPLACE INTO tone_detection_cache
        (numero, tone, is_fax, details, duration_ms, hangup_cause, amd_status, amd_cause,
         detected_at, expires_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result["numero"],
            result["tone"],
            1 if result.get("is_fax") else 0,
            result.get("details", ""),
            result.get("duration_ms", 0),
            result.get("hangup_cause", 0),
            result.get("amd_status", ""),
            result.get("amd_cause", ""),
            now.isoformat(),
            expires.isoformat(),
        ),
    )
    conn.commit()
    conn.close()


def get_all_cached_tones() -> List[Dict]:
    """Retourne tous les résultats en cache (même expirés)."""
    conn = _connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tone_detection_cache ORDER BY detected_at DESC")
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def clear_tone_cache(numero: Optional[str] = None) -> int:
    """Supprime le cache (un numéro ou tout)."""
    conn = _connect_db()
    cur = conn.cursor()
    if numero:
        cur.execute("DELETE FROM tone_detection_cache WHERE numero = ?", (numero,))
    else:
        cur.execute("DELETE FROM tone_detection_cache")
    count = cur.rowcount
    conn.commit()
    conn.close()
    return count


# ──────────────────────────────────────────────
# Moteur de classification
# ──────────────────────────────────────────────

class AsteriskEngine:
    """
    Moteur de classification des numéros de fax.
    
    Priorité de classification :
      1. Cache BDD : résultat d'un appel test précédent
      2. Plages SDA manuelles : préfixes configurés
      3. Appel test AMI : Originate + AMD/FaxDetect (si activé)
      4. Classification préfixe FR : fallback
    """

    def __init__(self):
        self._sda_ranges: List[Dict] = []
        self._ami_config: Optional[AMIConfig] = None
        self._ami_peers: List[str] = []
        self._loaded = False

    def load(self) -> None:
        """Charge la configuration depuis la BDD."""
        self._sda_ranges = get_sda_ranges()

        config = get_ami_config()
        self._ami_config = AMIConfig(
            host=config.get("ami_host", "127.0.0.1"),
            port=config.get("ami_port", 5038),
            username=config.get("ami_username", "admin"),
            secret=config.get("ami_secret", ""),
            enabled=bool(config.get("ami_enabled", 0)),
            context=config.get("ami_context", "faxcloud-detect"),
            caller_id=config.get("ami_caller_id", "FaxCloudTest"),
            call_timeout=config.get("ami_call_timeout", 15),
            detect_timeout=config.get("ami_detect_timeout", 10),
            trunk=config.get("ami_trunk", ""),
            cache_ttl_hours=config.get("cache_ttl_hours", 168),
        )

        # Si AMI activé, récupérer les peers
        if self._ami_config.enabled:
            self._load_ami_peers()

        self._loaded = True
        logger.info("AsteriskEngine chargé: %d plages SDA, AMI %s",
                     len(self._sda_ranges),
                     "activé" if self._ami_config.enabled else "désactivé")

    def _load_ami_peers(self) -> None:
        """Récupère les numéros SDA depuis Asterisk via AMI."""
        ami = AMIConnection(self._ami_config)
        if not ami.connect():
            return
        try:
            peers = ami.get_pjsip_endpoints()
            if not peers:
                peers = ami.get_sip_peers()

            for peer in peers:
                callerid = peer.get("Callerid", peer.get("CallerID", ""))
                match = re.search(r'<(\d+)>', callerid)
                if match:
                    self._ami_peers.append(match.group(1))
                obj_name = peer.get("ObjectName", peer.get("Endpoint", ""))
                if obj_name and obj_name.isdigit():
                    self._ami_peers.append(obj_name)

            logger.info("AMI: %d peers/endpoints récupérés", len(self._ami_peers))
        finally:
            ami.disconnect()

    def detect_tone(self, numero: str, force: bool = False) -> Dict:
        """
        Appelle un numéro et détecte la tonalité fax.
        
        Args:
            numero: Numéro normalisé (33XXXXXXXXX)
            force: Ignorer le cache et refaire l'appel
            
        Returns:
            Résultat de détection avec tone, is_fax, details, etc.
        """
        if not self._loaded:
            self.load()

        if not self._ami_config or not self._ami_config.enabled:
            return AMIConnection._error_result(numero, "AMI non activé")

        # Vérifier le cache
        if not force:
            cached = get_cached_tone(numero)
            if cached:
                logger.info("Cache hit pour %s: %s", numero, cached.get("tone"))
                cached["from_cache"] = True
                return cached

        # Appel test
        ami = AMIConnection(self._ami_config)
        if not ami.connect():
            return AMIConnection._error_result(numero, "Impossible de se connecter à Asterisk")

        try:
            result = ami.detect_fax_tone(numero)
        finally:
            ami.disconnect()

        # Sauvegarder en cache
        if result.get("tone") != TONE_ERROR:
            save_tone_cache(result, self._ami_config.cache_ttl_hours)

        result["from_cache"] = False
        return result

    def detect_tones_batch(self, numeros: List[str], force: bool = False,
                           on_progress=None) -> List[Dict]:
        """
        Détecte la tonalité pour une liste de numéros.
        Appelle un par un pour ne pas surcharger le PBX.
        
        Args:
            numeros: Liste de numéros normalisés
            force: Ignorer le cache
            on_progress: Callback(index, total, result) optionnel
        """
        results = []
        unique_numeros = list(dict.fromkeys(numeros))  # Déduplique en gardant l'ordre
        total = len(unique_numeros)

        for i, numero in enumerate(unique_numeros):
            result = self.detect_tone(numero, force=force)
            results.append(result)

            if on_progress:
                on_progress(i + 1, total, result)

            # Pause entre les appels pour ne pas surcharger
            if i < total - 1 and not result.get("from_cache"):
                time.sleep(2)

        return results

    def classify_number(self, numero_normalise: str) -> Tuple[str, str]:
        """
        Classifie un numéro normalisé (format 33XXXXXXXXX).
        
        Priorité :
          1. Cache de détection de tonalité (résultat d'appel réel)
          2. Plages SDA manuelles
          3. Peers AMI
          4. Classification par préfixe français
        """
        if not self._loaded:
            self.load()

        if not numero_normalise or len(numero_normalise) < 4:
            return NUMBER_TYPE_UNKNOWN, NUMBER_TYPE_LABELS[NUMBER_TYPE_UNKNOWN]

        # 1. Vérifier le cache de détection de tonalité
        cached = get_cached_tone(numero_normalise)
        if cached:
            return self._tone_to_type(cached.get("tone", ""), cached.get("is_fax", False))

        # 2. Vérifier dans les plages SDA configurées
        if self._is_sda_by_range(numero_normalise):
            return NUMBER_TYPE_SDA, NUMBER_TYPE_LABELS[NUMBER_TYPE_SDA]

        # 3. Vérifier dans les peers AMI
        if self._is_sda_by_ami(numero_normalise):
            return NUMBER_TYPE_SDA, NUMBER_TYPE_LABELS[NUMBER_TYPE_SDA]

        # 4. Classification par préfixe français
        return self._classify_french_number(numero_normalise)

    @staticmethod
    def _tone_to_type(tone: str, is_fax: bool) -> Tuple[str, str]:
        """Convertit un résultat de détection en type de numéro."""
        if is_fax or tone == TONE_FAX:
            return NUMBER_TYPE_SDA_FAX, NUMBER_TYPE_LABELS[NUMBER_TYPE_SDA_FAX]
        elif tone == TONE_VOICE:
            return NUMBER_TYPE_PHONE, NUMBER_TYPE_LABELS[NUMBER_TYPE_PHONE]
        elif tone == TONE_BUSY:
            return NUMBER_TYPE_BUSY, NUMBER_TYPE_LABELS[NUMBER_TYPE_BUSY]
        elif tone == TONE_NO_ANSWER:
            return NUMBER_TYPE_NO_ANSWER, NUMBER_TYPE_LABELS[NUMBER_TYPE_NO_ANSWER]
        elif tone == TONE_ERROR:
            return NUMBER_TYPE_ERROR, NUMBER_TYPE_LABELS[NUMBER_TYPE_ERROR]
        return NUMBER_TYPE_UNKNOWN, NUMBER_TYPE_LABELS[NUMBER_TYPE_UNKNOWN]

    def _is_sda_by_range(self, numero: str) -> bool:
        """Vérifie si le numéro appartient à une plage SDA configurée."""
        for sda in self._sda_ranges:
            prefix = sda.get("prefix", "")
            if not prefix:
                continue

            if not numero.startswith(prefix):
                continue

            # Si pas de range défini, le prefix seul suffit
            range_start = sda.get("range_start", "")
            range_end = sda.get("range_end", "")

            if not range_start and not range_end:
                return True

            # Extraire la partie après le préfixe
            suffix = numero[len(prefix):]
            if not suffix:
                return True

            # Comparer avec la plage
            if range_start and range_end:
                try:
                    s = int(suffix.ljust(len(range_start), '0'))
                    r_start = int(range_start)
                    r_end = int(range_end)
                    if r_start <= s <= r_end:
                        return True
                except (ValueError, TypeError):
                    pass
            elif range_start:
                if suffix.startswith(range_start):
                    return True

        return False

    def _is_sda_by_ami(self, numero: str) -> bool:
        """Vérifie si le numéro correspond à un peer Asterisk."""
        if not self._ami_peers:
            return False
        # Comparaison directe et avec préfixe 33
        for peer in self._ami_peers:
            if numero == peer or numero.endswith(peer) or peer.endswith(numero[-9:]):
                return True
        return False

    @staticmethod
    def _classify_french_number(numero: str) -> Tuple[str, str]:
        """Classification selon les préfixes téléphoniques français."""
        if not numero.startswith("33"):
            return NUMBER_TYPE_INTERNATIONAL, NUMBER_TYPE_LABELS[NUMBER_TYPE_INTERNATIONAL]

        # Numéro français sans le 33 : 9 chiffres
        local = numero[2:]  # ex: "493095562"

        if not local:
            return NUMBER_TYPE_UNKNOWN, NUMBER_TYPE_LABELS[NUMBER_TYPE_UNKNOWN]

        first_digit = local[0]

        # Numéros courts (3xxx, 10xx, 11x, etc.)
        if len(local) <= 6:
            return NUMBER_TYPE_SHORT, NUMBER_TYPE_LABELS[NUMBER_TYPE_SHORT]

        # Mobile : 06, 07
        if first_digit in ("6", "7"):
            return NUMBER_TYPE_MOBILE, NUMBER_TYPE_LABELS[NUMBER_TYPE_MOBILE]

        # Spécial : 08
        if first_digit == "8":
            return NUMBER_TYPE_SPECIAL, NUMBER_TYPE_LABELS[NUMBER_TYPE_SPECIAL]

        # Géographique : 01-05, 09
        if first_digit in ("1", "2", "3", "4", "5", "9"):
            return NUMBER_TYPE_GEOGRAPHIC, NUMBER_TYPE_LABELS[NUMBER_TYPE_GEOGRAPHIC]

        return NUMBER_TYPE_UNKNOWN, NUMBER_TYPE_LABELS[NUMBER_TYPE_UNKNOWN]

    def classify_entries(self, entries: List[Dict]) -> List[Dict]:
        """
        Enrichit une liste d'entrées fax avec le type de numéro.
        
        Ajoute les champs:
          - numero_type: code du type (sda, geographic, mobile, etc.)
          - numero_type_label: label français
        """
        if not self._loaded:
            self.load()

        for entry in entries:
            numero = entry.get("numero_normalise", "")
            num_type, num_label = self.classify_number(numero)
            entry["numero_type"] = num_type
            entry["numero_type_label"] = num_label

        return entries

    def classify_entries_with_asterisk_detection(self, entries: List[Dict], enable_detection: bool = False) -> List[Dict]:
        """
        Enrichit les entrées avec détection Asterisk réelle (optional).
        
        Si enable_detection=True et AMI activé :
          - Appelle Asterisk pour chaque numéro unique
          - Ajoute : asterisk_tone, asterisk_is_fax, asterisk_duration_ms, asterisk_hangup_cause
          - Classifie basé sur le résultat de détection
        
        Si enable_detection=False :
          - Classifie par la méthode standard (cache + plages SDA + préfixe)
        
        Args:
            entries: Liste des entrées à classifier
            enable_detection: Activer la détection Asterisk réelle
        
        Returns:
            Entries enrichies avec numero_type, numero_type_label et optionnellement asterisk_*
        """
        if not self._loaded:
            self.load()

        # Phase 1 : Classification standard (rapide)
        entries = self.classify_entries(entries)
        
        # Phase 2 : Détection Asterisk si activée
        if not enable_detection or not self._config.get("ami_enabled"):
            return entries

        logger.info("Détection Asterisk en temps réel pour %d entrées", len(entries))
        
        # Déduplique les numéros à analyser
        unique_numeros = {}
        for entry in entries:
            numero = entry.get("numero_normalise", "")
            if numero and numero not in unique_numeros:
                unique_numeros[numero] = True
        
        # Détecte chaque numéro unique
        detection_results = {}
        for idx, numero in enumerate(unique_numeros.keys(), 1):
            try:
                result = self.detect_tone(numero)
                detection_results[numero] = result
                logger.debug("Détection %d/%d: %s → %s (fax=%s)",
                            idx, len(unique_numeros), numero, result.get("tone"), result.get("is_fax"))
                # Petit délai entre les appels pour ne pas surcharger Asterisk
                if idx < len(unique_numeros):
                    time.sleep(1)
            except Exception as e:
                logger.warning("Erreur détection %s: %s", numero, e)
                detection_results[numero] = {
                    "tone": "error",
                    "is_fax": False,
                    "duration_ms": 0,
                    "details": str(e)
                }
        
        # Phase 3 : Enrichit les entrées avec les résultats
        for entry in entries:
            numero = entry.get("numero_normalise", "")
            if numero in detection_results:
                result = detection_results[numero]
                
                # Ajoute les champs Asterisk
                entry["asterisk_tone"] = result.get("tone", "")
                entry["asterisk_is_fax"] = result.get("is_fax", False)
                entry["asterisk_duration_ms"] = result.get("duration_ms", 0)
                entry["asterisk_hangup_cause"] = result.get("hangup_cause", 0)
                entry["asterisk_amd_status"] = result.get("amd_status", "")
                entry["asterisk_detected"] = True
                
                # Reclassifie si Asterisk a donné un résultat valide
                if result.get("tone") and result.get("tone") != "error":
                    num_type, num_label = self._tone_to_type(result.get("tone", ""), result.get("is_fax", False))
                    entry["numero_type"] = num_type
                    entry["numero_type_label"] = num_label
                    entry["numero_type_source"] = "asterisk_detection"
                else:
                    entry["numero_type_source"] = "fallback"
            else:
                entry["asterisk_detected"] = False
                entry["numero_type_source"] = "cache_or_prefix"
        
        logger.info("Détection Asterisk complétée: %d numéros analysés", len(detection_results))
        return entries

    def get_stats(self, entries: List[Dict]) -> Dict:
        """Calcule les statistiques SDA/Téléphone à partir des entrées classifiées."""
        stats = {
            "total": len(entries),
            "sda": 0,
            "sda_fax": 0,
            "telephone": 0,
            "mobile": 0,
            "international": 0,
            "special": 0,
            "no_answer": 0,
            "busy": 0,
            "error": 0,
            "unknown": 0,
            "par_type": {},
        }

        for entry in entries:
            num_type = entry.get("numero_type", NUMBER_TYPE_UNKNOWN)
            stats["par_type"][num_type] = stats["par_type"].get(num_type, 0) + 1

            if num_type == NUMBER_TYPE_SDA:
                stats["sda"] += 1
            elif num_type == NUMBER_TYPE_SDA_FAX:
                stats["sda_fax"] += 1
            elif num_type in (NUMBER_TYPE_GEOGRAPHIC, NUMBER_TYPE_PHONE):
                stats["telephone"] += 1
            elif num_type == NUMBER_TYPE_MOBILE:
                stats["mobile"] += 1
            elif num_type == NUMBER_TYPE_INTERNATIONAL:
                stats["international"] += 1
            elif num_type == NUMBER_TYPE_SPECIAL:
                stats["special"] += 1
            elif num_type == NUMBER_TYPE_NO_ANSWER:
                stats["no_answer"] += 1
            elif num_type == NUMBER_TYPE_BUSY:
                stats["busy"] += 1
            elif num_type == NUMBER_TYPE_ERROR:
                stats["error"] += 1
            else:
                stats["unknown"] += 1

        total = stats["total"] or 1
        stats["pct_sda"] = round(stats["sda"] / total * 100, 1)
        stats["pct_sda_fax"] = round(stats["sda_fax"] / total * 100, 1)
        stats["pct_telephone"] = round(stats["telephone"] / total * 100, 1)
        stats["pct_mobile"] = round(stats["mobile"] / total * 100, 1)

        stats["par_type_labels"] = {
            k: NUMBER_TYPE_LABELS.get(k, k) for k in stats["par_type"]
        }

        return stats


# ──────────────────────────────────────────────
# Instance globale
# ──────────────────────────────────────────────

_engine: Optional[AsteriskEngine] = None


def get_engine() -> AsteriskEngine:
    global _engine
    if _engine is None:
        _engine = AsteriskEngine()
        _engine.load()
    return _engine


def reload_engine() -> AsteriskEngine:
    global _engine
    _engine = AsteriskEngine()
    _engine.load()
    return _engine


# ──────────────────────────────────────────────
# Dialplan Asterisk (snippet à copier dans extensions.conf)
# ──────────────────────────────────────────────

DIALPLAN_SNIPPET = """
; ==============================================
; FaxCloud Analyzer - Contexte de détection fax
; À ajouter dans /etc/asterisk/extensions.conf
; ==============================================

[faxcloud-detect]
; Extension appelée par l'Originate AMI
; Décroche, lance AMD avec détection fax, attend, raccroche

exten => detect,1,Answer()
 same => n,Set(FAXCLOUD_TEST=1)
 same => n,AMD(2500,2000,2500,3000,1100,256,25,3)
 ; Paramètres AMD :
 ;   initial_silence=2500ms
 ;   greeting=2000ms  
 ;   after_greeting_silence=2500ms
 ;   total_analysis_time=3000ms
 ;   min_word_length=1100ms (détecte CNG comme "mot long")
 ;   between_words_silence=256ms
 ;   maximum_number_of_words=25
 ;   silence_threshold=3
 same => n,Set(CDR(amdstatus)=${AMDSTATUS})
 same => n,Set(CDR(amdcause)=${AMDCAUSE})
 same => n,GotoIf($["${AMDSTATUS}" = "MACHINE"]?fax_check:voice_detected)

 ; Vérification supplémentaire par FaxDetect
 same => n(fax_check),Wait(1)
 same => n,Set(FAXDETECT(t38)=yes)
 same => n,Set(FAXDETECT(cng)=yes)
 same => n,Set(FAXOPT(faxdetect)=both)
 same => n,Wait(${IF($[${DETECT_TIMEOUT}]?${DETECT_TIMEOUT}:5)})
 same => n,Set(FAXDETECTED=${IF($["${FAXSTATUS}" = "SUCCESS"]?1:0)})
 same => n,Hangup()

 same => n(voice_detected),Set(FAXDETECTED=0)
 same => n,Hangup()

; Catch-all pour les appels entrants dans ce contexte
exten => _X.,1,Goto(detect,1)
exten => h,1,NoOp(Appel terminé - AMDSTATUS=${AMDSTATUS} FAXDETECTED=${FAXDETECTED})
"""


def get_dialplan_snippet() -> str:
    """Retourne le snippet de dialplan Asterisk à configurer."""
    return DIALPLAN_SNIPPET.strip()

