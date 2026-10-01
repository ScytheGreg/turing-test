from pathlib import Path

from faster_whisper import WhisperModel

from app.config import WHISPER_LANGUAGE, WHISPER_MODEL


class WhisperSTT:
    def __init__(self) -> None:
        self.model = WhisperModel(
            WHISPER_MODEL,
            device="cuda",
            compute_type="float16",
        )

    def transcribe(self, audio_path: Path) -> str:
        segments, _ = self.model.transcribe(
            str(audio_path),
            language=WHISPER_LANGUAGE,
        )

        text = " ".join(segment.text.strip() for segment in segments).strip()

        if not text:
            raise RuntimeError("Whisper nie rozpoznał żadnej wypowiedzi.")

        return text
