import os
from pathlib import Path

SESSIONS_DIR = Path.home() / "Library" / "Application Support" / "OpenOats" / "sessions"

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY", "")
MODEL = "claude-haiku-4-5-20251001"

# How many utterances to buffer before sending to Claude
CHUNK_SIZE = 3

# How long to wait (seconds) after the last utterance before flushing a partial chunk
DEBOUNCE_SECONDS = 8.0

# How often to poll the transcript file for new lines (seconds)
POLL_INTERVAL = 0.5
