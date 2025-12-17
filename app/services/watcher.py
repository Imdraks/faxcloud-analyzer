import asyncio
import logging
from pathlib import Path

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from app.core.settings import settings

logger = logging.getLogger(__name__)

observer: Observer | None = None


class InboxHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        logger.info("Nouveau fichier détecté dans l'inbox: %s", event.src_path)
        # L'import automatique peut être branché ici (appel service/API)


async def start_watcher():
    global observer
    if not settings.watch_inbox:
        return
    handler = InboxHandler()
    observer = Observer()
    observer.schedule(handler, str(settings.inbox_path), recursive=False)
    observer.start()
    logger.info("Watchdog démarré sur %s", settings.inbox_path)


async def stop_watcher():
    global observer
    if observer:
        observer.stop()
        observer.join()
        observer = None
