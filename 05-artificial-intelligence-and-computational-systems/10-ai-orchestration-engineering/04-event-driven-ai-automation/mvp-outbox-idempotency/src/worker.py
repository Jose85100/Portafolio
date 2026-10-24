"""Hard process-exit injection used by integration tests."""

import sys
from pathlib import Path

from src.engine import dispatch

if __name__ == "__main__":
    dispatch(Path(sys.argv[1]), Path(sys.argv[2]), sys.argv[3], sys.argv[4], True, True)
