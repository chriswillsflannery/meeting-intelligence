"""
Terminal display for meeting intelligence output.
"""

import sys
from datetime import datetime


DIVIDER = "─" * 60
HEADER_COLOR = "\033[1;36m"   # bold cyan
SIGNAL_COLOR = "\033[1;33m"   # bold yellow
RESET = "\033[0m"
DIM = "\033[2m"


def print_header(mode: str) -> None:
    print(f"\n{HEADER_COLOR}{DIVIDER}")
    print(f"  Meeting Intelligence  [{mode.upper()} MODE]")
    print(f"{DIVIDER}{RESET}\n")


def print_chunk_header(utterances: list[dict]) -> None:
    speakers = list(dict.fromkeys(u.get("speaker", "?") for u in utterances))
    ts = utterances[0].get("timestamp", "")[:19].replace("T", " ")
    print(f"\n{DIM}── {ts}  [{', '.join(speakers)}] ──────{RESET}")


def stream_enrichment(token: str) -> None:
    """Write a streaming token directly to stdout."""
    if token == "--":
        return
    sys.stdout.write(token)
    sys.stdout.flush()


def print_enrichment_end() -> None:
    print()  # newline after streaming completes


def print_no_signal() -> None:
    print(f"{DIM}  (no signal){RESET}")


def print_error(msg: str) -> None:
    print(f"\033[1;31m[error] {msg}{RESET}")


def print_status(msg: str) -> None:
    print(f"{DIM}[{msg}]{RESET}")
