#!/usr/bin/env python3
"""
Meeting Intelligence Overlay
Tails OpenOats live transcripts and streams Claude enrichment to the terminal.

Usage:
    python main.py --mode finance
    python main.py --mode general
"""

import argparse
import threading
import time
import sys
from collections import deque

import config
import display
import enricher
import watcher
from modes import finance, general


def get_mode(name: str):
    if name == "finance":
        return finance
    elif name == "general":
        return general
    else:
        print(f"Unknown mode: {name}. Choose 'finance' or 'general'.")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Meeting Intelligence Overlay")
    parser.add_argument(
        "--mode",
        choices=["finance", "general"],
        default="general",
        help="Enrichment mode (default: general)",
    )
    args = parser.parse_args()

    mode = get_mode(args.mode)

    display.print_header(args.mode)

    # Buffer for incoming utterances
    buffer: deque[dict] = deque()
    buffer_lock = threading.Lock()
    last_utterance_time: list[float] = [0.0]  # mutable container for thread access

    def on_utterance(utterance: dict) -> None:
        with buffer_lock:
            buffer.append(utterance)
            last_utterance_time[0] = time.monotonic()

    # Start watcher in background thread
    watch_thread = threading.Thread(target=watcher.watch, args=(on_utterance,), daemon=True)
    watch_thread.start()

    # Main loop: flush buffer when chunk_size reached OR debounce timeout
    try:
        while True:
            time.sleep(0.2)

            with buffer_lock:
                buf_size = len(buffer)
                elapsed = time.monotonic() - last_utterance_time[0]
                should_flush = (
                    buf_size >= config.CHUNK_SIZE
                    or (buf_size > 0 and elapsed >= config.DEBOUNCE_SECONDS)
                )
                if should_flush:
                    chunk = list(buffer)
                    buffer.clear()
                else:
                    chunk = []

            if chunk:
                display.print_chunk_header(chunk)
                accumulated = []

                def on_token(token: str):
                    accumulated.append(token)
                    display.stream_enrichment(token)

                try:
                    enricher.enrich(chunk, mode.SYSTEM_PROMPT, on_token)
                    display.print_enrichment_end()
                    full = "".join(accumulated).strip()
                    if full == "--":
                        display.print_no_signal()
                except Exception as e:
                    display.print_error(str(e))

    except KeyboardInterrupt:
        print("\n\n[done]")


if __name__ == "__main__":
    main()
