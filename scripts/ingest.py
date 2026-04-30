import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from knowledge_vault.cli import ingest_main


if __name__ == "__main__":
    ingest_main()
