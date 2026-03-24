"""
Sends buffered transcript chunks to Claude and streams the enrichment back.
"""

import anthropic
from pathlib import Path

from config import ANTHROPIC_API_KEY, MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

VAULT_DIR = Path(__file__).parent.parent  # ~/Chris Dev/


def _load_vault_context() -> str:
    """
    Load lightweight context from the vault to ground Claude's enrichment.
    Reads AgentSmyth.md (company context) if it exists.
    """
    context_parts = []

    company_note = VAULT_DIR / "AgentSmyth.md"
    if company_note.exists():
        content = company_note.read_text().strip()
        if content:
            context_parts.append(f"<company_context>\n{content}\n</company_context>")

    return "\n\n".join(context_parts)


def enrich(utterances: list[dict], system_prompt: str, on_token: callable) -> None:
    """
    Send a chunk of utterances to Claude and stream enrichment tokens to on_token().
    utterances: list of {"timestamp": ..., "text": ..., "speaker": ...}
    """
    transcript_text = "\n".join(
        f"[{u.get('speaker', 'unknown')}]: {u['text']}" for u in utterances
    )

    vault_context = _load_vault_context()

    full_system = system_prompt
    if vault_context:
        full_system = f"{vault_context}\n\n{system_prompt}"

    with client.messages.stream(
        model=MODEL,
        max_tokens=300,
        system=full_system,
        messages=[
            {
                "role": "user",
                "content": f"<transcript_chunk>\n{transcript_text}\n</transcript_chunk>",
            }
        ],
    ) as stream:
        for text in stream.text_stream:
            on_token(text)
