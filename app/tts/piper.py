import subprocess
import tempfile
from pathlib import Path

from app.config import PIPER_LENGTH_SCALE, PIPER_MODELS


import subprocess
import tempfile
from pathlib import Path

from app.config import PIPER_LENGTH_SCALE, PIPER_MODELS


class PiperTTS:
    def __init__(self) -> None:
        for voice, model_path in PIPER_MODELS.items():
            if not model_path.exists():
                raise FileNotFoundError(
                    f"Nie znaleziono modelu Piper dla głosu "
                    f"{voice}: {model_path}"
                )

    def synthesize(
        self,
        text: str,
        voice: str = "alice",
    ) -> Path:
        if not text.strip():
            raise ValueError("Tekst do syntezy nie może być pusty.")

        if voice not in PIPER_MODELS:
            raise ValueError(
                f"Nieznany głos: {voice}. "
                f"Dostępne: {', '.join(PIPER_MODELS)}"
            )

        model_path = PIPER_MODELS[voice]

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            output_path = Path(temp_file.name)

        subprocess.run(
            [
                "piper",
                "--model",
                str(model_path),
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