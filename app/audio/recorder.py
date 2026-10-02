from pathlib import Path
import tempfile

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

from app.config import MIC_CHANNELS, MIC_DEVICE_NAME, SAMPLE_RATE


class AudioRecorder:
    def __init__(self) -> None:
        self._stream: sd.InputStream | None = None
        self._chunks: list[np.ndarray] = []

    @property
    def is_recording(self) -> bool:
        return self._stream is not None

    def _callback(
        self,
        indata: np.ndarray,
        frames: int,
        time,
        status,
    ) -> None:
        if status:
            print(f"Audio status: {status}")

        self._chunks.append(indata.copy())

    def _find_microphone(self) -> str:
        try:
            device = sd.query_devices(
                MIC_DEVICE_NAME,
                kind="input",
            )
        except Exception as exc:
            raise RuntimeError(
                f"Nie znaleziono mikrofonu zawierającego nazwę "
                f"'{MIC_DEVICE_NAME}'."
            ) from exc

        if device["max_input_channels"] < MIC_CHANNELS:
            raise RuntimeError(
                f"Urządzenie '{device['name']}' nie ma wystarczającej "
                f"liczby kanałów wejściowych. "
                f"Wymagane: {MIC_CHANNELS}, "
                f"dostępne: {device['max_input_channels']}."
            )

        print(
            f"Mikrofon: {device['name']} "
            f"(input channels: {device['max_input_channels']})"
        )

        return device["name"]

    def start(self) -> None:
        if self.is_recording:
            raise RuntimeError("Nagrywanie już trwa.")

        self._chunks = []

        microphone = self._find_microphone()

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=MIC_CHANNELS,
            dtype="int16",
            device=microphone,
            callback=self._callback,
        )

        self._stream.start()

    def stop(self) -> Path:
        if not self.is_recording:
            raise RuntimeError("Nagrywanie nie jest aktywne.")

        stream = self._stream
        self._stream = None

        stream.stop()
        stream.close()

        if not self._chunks:
            raise RuntimeError("Nagranie jest puste.")

        audio = np.concatenate(self._chunks, axis=0)

        with tempfile.NamedTemporaryFile(
            suffix=".wav",
            delete=False,
        ) as temp_file:
            output_path = Path(temp_file.name)

        write(output_path, SAMPLE_RATE, audio)

        return output_path


def record(duration: float) -> Path:
    """Record audio for a fixed duration."""
    if duration <= 0:
        raise ValueError("Duration must be greater than zero.")

    recorder = AudioRecorder()
    recorder.start()

    sd.sleep(int(duration * 1000))

    return recorder.stop()