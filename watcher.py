"""
Watches the OpenOats sessions directory for the active session,
then tails transcript.live.jsonl and yields new utterances.
"""

import json
import time
from pathlib import Path
from typing import Callable, Optional

from config import SESSIONS_DIR, POLL_INTERVAL


def _latest_session_dir() -> Optional[Path]:
    """Return the most recently modified session directory, or None."""
    dirs = [d for d in SESSIONS_DIR.iterdir() if d.is_dir() and d.name.startswith("session_")]
    if not dirs:
        return None
    return max(dirs, key=lambda d: d.stat().st_mtime)


def watch(on_utterance: Callable[[dict], None]) -> None:
    """
    Continuously monitors for an active OpenOats session and emits utterances.
    Calls on_utterance({"timestamp": ..., "text": ..., "speaker": ...}) for each new line.
    Blocks forever — run in a thread or use Ctrl+C to exit.
    """
    print(f"[watcher] Monitoring: {SESSIONS_DIR}")
    print("[watcher] Waiting for an OpenOats session to start...")

    current_session: Optional[Path] = None
    transcript_path: Optional[Path] = None
    file_position: int = 0

    while True:
        latest = _latest_session_dir()

        # New session detected
        if latest and latest != current_session:
            current_session = latest
            transcript_path = current_session / "transcript.live.jsonl"
            file_position = 0
            print(f"\n[watcher] Session: {current_session.name}")
            print(f"[watcher] Tailing: {transcript_path.name}\n")

        # Tail the active transcript
        if transcript_path and transcript_path.exists():
            with open(transcript_path, "r") as f:
                f.seek(file_position)
                new_lines = f.readlines()
                file_position = f.tell()

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue
                try:
                    utterance = json.loads(line)
                    on_utterance(utterance)
                except json.JSONDecodeError:
                    pass

        time.sleep(POLL_INTERVAL)
