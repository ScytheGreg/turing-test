from enum import Enum

from app.audio.recorder import AudioRecorder
from app.conversation.service import ConversationService
from app.stt.whisper import WhisperSTT
from pathlib import Path

from app.tts.piper import PiperTTS


class ConversationState(Enum):
    IDLE = "idle"
    RECORDING = "recording"
    TRANSCRIBING = "transcribing"
    REVIEW = "review"
    SENDING = "sending"


class ConversationController:
    def __init__(
            self,
            recorder: AudioRecorder | None = None,
            stt: WhisperSTT | None = None,
            conversation: ConversationService | None = None,
            tts: PiperTTS | None = None,
    ) -> None:
        self.recorder = recorder or AudioRecorder()
        self.stt = stt or WhisperSTT()
        self.conversation = conversation or ConversationService()
        self.tts = tts or PiperTTS()

        self.state = ConversationState.IDLE
        self.transcript: str | None = None
        self.answer: str | None = None
        self.audio_path: Path | None = None

    def start_recording(self) -> None:
        if self.state != ConversationState.IDLE:
            raise RuntimeError(
                f"Nie można rozpocząć nagrywania w stanie: {self.state.value}"
            )

        self.transcript = None
        self.answer = None

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

    def edit_transcript(self, text: str) -> None:
        if self.state != ConversationState.REVIEW:
            raise RuntimeError(
                f"Nie można edytować transkrypcji w stanie: {self.state.value}"
            )

        text = text.strip()

        if not text:
            raise ValueError("Transkrypcja nie może być pusta.")

        self.transcript = text

    def send(self) -> str:
        if self.state != ConversationState.REVIEW:
            raise RuntimeError(
                f"Nie można wysłać wiadomości w stanie: {self.state.value}"
            )

        if not self.transcript:
            raise RuntimeError("Brak transkrypcji do wysłania.")

        self.state = ConversationState.SENDING

        try:
            answer = self.conversation.send(self.transcript)
            audio_path = self.tts.synthesize(answer)
        except Exception:
            self.state = ConversationState.REVIEW
            raise

        self.answer = answer
        self.audio_path = audio_path
        self.state = ConversationState.IDLE

        return answer

    def cancel(self) -> None:
        if self.state == ConversationState.RECORDING:
            self.recorder.stop()

        self.transcript = None
        self.answer = None
        self.audio_path = None
        self.state = ConversationState.IDLE

