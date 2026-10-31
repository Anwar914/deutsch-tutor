"""Text-to-speech for public lesson text; never uploads microphone audio."""

from io import BytesIO


def synthesize(text: str) -> bytes:
    """Return German MP3 bytes with bounded network timeouts."""
    from gtts import gTTS

    if not text.strip() or len(text) > 8000:
        raise ValueError("Invalid speech text")
    buffer = BytesIO()
    gTTS(text=text, lang="de", slow=True, timeout=(5, 20)).write_to_fp(buffer)
    return buffer.getvalue()
