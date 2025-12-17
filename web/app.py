#!/usr/bin/env python3
"""Wrapper historique.

Le serveur web canonique est maintenant `src.server` (app factory + routes pages + API).
On garde ce fichier pour compat avec `run_web.bat`/anciens usages.
"""

from __future__ import annotations

import argparse

from src.server import create_app


def main() -> None:
    parser = argparse.ArgumentParser(description="FaxCloud Analyzer - web (legacy wrapper)")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
