#!/usr/bin/env python3

import logging

from cli import app

logging.basicConfig(
    level=logging.WARNING,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("orchestrator").setLevel(logging.DEBUG)

if __name__ == "__main__":
    app()
