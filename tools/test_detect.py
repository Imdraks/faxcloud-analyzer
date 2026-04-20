"""Test rapide de la détection de tonalité fax."""
import requests
import json

print("=== Test détection de tonalité ===")
print()

numeros = ["0493095562", "0493095100", "0176543210", "0612345678", "0493095200"]

for n in numeros:
    r = requests.post(
        "http://127.0.0.1:8000/api/asterisk/detect",
        json={"numero": n},
        timeout=30,
    )
    d = r.json()
    fax = "FAX" if d.get("is_fax") else "---"
    tone = d.get("tone", "?")
    details = d.get("details", "")
    ms = d.get("duration_ms", 0)
    cached = " (cache)" if d.get("from_cache") else ""
    print(f"  {n:15s} | {fax:4s} | {tone:12s} | {ms:5d}ms | {details}{cached}")

print()
print("=== Cache ===")
r2 = requests.get("http://127.0.0.1:8000/api/asterisk/cache", timeout=5)
cache = r2.json()
print(f"  {cache['count']} résultats en cache")
for entry in cache.get("cache", []):
    print(f"    {entry['numero']} → {entry['tone']} (expire: {entry['expires_at'][:10]})")
