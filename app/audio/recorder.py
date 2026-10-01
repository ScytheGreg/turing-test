from pathlib import Path
import tempfile

import sounddevice as sd
from scipy.io.wavfile import write

from app.config import MIC_DEVICE, SAMPLE_RATE


def record(duration: float) -> Path:
    """Record audio from the configured microphone and return WAV path."""
    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    audio = sd.rec(
        int(duration * SAMPLE_RATE),
        samplerate=SAMPLE_RATE,
        channels=1,
        dtype="int16",
        device=MIC_DEVICE,
    )
    sd.wait()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        output_path = Path(temp_file.name)

    write(output_path, SAMPLE_RATE, audio)

    return output_path
