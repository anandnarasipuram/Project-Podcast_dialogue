"""
Podcast Studio — text-to-speech step.
Author: Nnanyelugo Ahukannah

Turns the recap script into an audio file using OpenAI's TTS API. For monologues,
streams the response straight to disk so we never hold the whole audio in memory.
For dialogues, synthesises each speaker turn separately (with an alternating
voice) and stitches the clips into one mp3.
"""

from __future__ import annotations

from pathlib import Path

from openai import OpenAI

TTS_MODEL = "tts-1"
VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
DEFAULT_VOICE = "nova"


class TTSError(RuntimeError):
    """Raised for any text-to-speech problem, so the UI can show a clean message."""


def generate_audio(client: OpenAI, text: str, out_path: Path, voice: str = DEFAULT_VOICE) -> Path:
    """Synthesise `text` to an mp3 at `out_path` and return the path."""
    if not text or not text.strip():
        raise TTSError("Nothing to speak - the recap script is empty.")
    if voice not in VOICES:
        voice = DEFAULT_VOICE

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with client.audio.speech.with_streaming_response.create(
            model=TTS_MODEL, voice=voice, input=text
        ) as response:
            response.stream_to_file(out_path)
    except Exception as exc:
        raise TTSError(f"Text-to-speech failed: {exc}") from exc
    return out_path


def generate_dialogue_audio(client: OpenAI, turns, out_path: Path,
                             voice_a: str = "nova", voice_b: str = "onyx") -> Path:
    """Synthesise each dialogue turn with an alternating voice and stitch into one mp3.

    Requires ffmpeg on the system PATH (pydub shells out to it for the mp3 export).
    """
    from pydub import AudioSegment
    import tempfile

    if not turns:
        raise TTSError("Nothing to speak - the dialogue script is empty.")

    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    combined = AudioSegment.empty()
    pause = AudioSegment.silent(duration=300)  # short gap between speakers

    with tempfile.TemporaryDirectory() as tmp:
        for i, turn in enumerate(turns):
            voice = voice_a if turn.speaker == "A" else voice_b
            snippet_path = Path(tmp) / f"turn_{i}.mp3"
            try:
                with client.audio.speech.with_streaming_response.create(
                    model=TTS_MODEL, voice=voice, input=turn.line
                ) as response:
                    response.stream_to_file(snippet_path)
            except Exception as exc:
                raise TTSError(f"Text-to-speech failed on turn {i}: {exc}") from exc
            combined += AudioSegment.from_mp3(snippet_path) + pause

    try:
        combined.export(out_path, format="mp3")
    except Exception as exc:
        raise TTSError(f"Couldn't assemble the dialogue audio: {exc}") from exc
    return out_path
