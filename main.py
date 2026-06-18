#!/usr/bin/env python3

import logging
import sys

from cli import app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)-5s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    stream=sys.stderr,
)
logging.getLogger("orchestrator").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)

if __name__ == "__main__":
    app()
