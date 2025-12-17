import logging
from pathlib import Path

import qrcode

from app.core.settings import settings

logger = logging.getLogger(__name__)


def generate_qr(public_token: str) -> Path:
    img = qrcode.make(f"/r/{public_token}")
    out_path = settings.qrcodes_dir / f"{public_token}.png"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path)
    logger.info("QR généré: %s", out_path)
    return out_path
