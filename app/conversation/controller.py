from enum import Enum
from pathlib import Path

from app.audio.recorder import AudioRecorder
from app.conversation.service import ConversationService
from app.stt.whisper import WhisperSTT


class ConversationState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    REVIEW = "review"


class ConversationController:
    def __init__(
        self,
        recorder: AudioRecorder | None = None,
        stt: WhisperSTT | None = None,
        conversation: ConversationService | None = None,
    ) -> None:
        self.recorder = recorder or AudioRecorder()
        self.stt = stt or WhisperSTT()
        self.conversation = conversation or ConversationService()

        self.state = ConversationState.IDLE
        self.transcript: str | None = None

    def start_recording(self) -> None:
        if self.state != ConversationState.IDLE:
            raise RuntimeError(
                f"Nie można rozpocząć nagrywania w stanie: {self.state.value}"
            )

        self.transcript = None
        self.recorder.start()
        self.state = ConversationState.RECORDING

    def stop_recording(self) -> str:
        if self.state != ConversationState.RECORDING:
            raise RuntimeError(
                f"Nie można zatrzymać nagrywania w stanie: {self.state.value}"
            )

        audio_path = self.recorder.stop()
        self.state = ConversationState.TRANSCRIBING

        try:
            transcript = self.stt.transcribe(audio_path)
        finally:
            audio_path.unlink(missing_ok=True)

        self.transcript = transcript
        self.state = ConversationState.REVIEW

        return transcript

    def cancel(self) -> None:
        if self.state == ConversationState.RECORDING:
            self.recorder.stop()

        self.transcript = None
        self.state = ConversationState.IDLE
