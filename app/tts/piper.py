import subprocess
import tempfile
from pathlib import Path

from app.config import PIPER_LENGTH_SCALE, PIPER_MODEL


class PiperTTS:
    def __init__(self) -> None:
        if not PIPER_MODEL.exists():
            raise FileNotFoundError(
                f"Nie znaleziono modelu Piper: {PIPER_MODEL}"
            )

    def synthesize(self, text: str) -> Path:
        if not text.strip():
            raise ValueError("Tekst do syntezy nie może być pusty.")

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            output_path = Path(temp_file.name)

        subprocess.run(
            [
                "piper",
                "--model",
                str(PIPER_MODEL),
                "--output_file",
                str(output_path),
                "--length-scale",
                str(PIPER_LENGTH_SCALE),
            ],
            input=text,
            text=True,
            check=True,
        )

        return output_path
