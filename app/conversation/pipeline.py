from pathlib import Path

from app.audio.recorder import record
from app.conversation.service import ConversationService
from app.stt.whisper import WhisperSTT
from app.tts.piper import PiperTTS


class ConversationPipeline:
    def __init__(
        self,
        stt: WhisperSTT | None = None,
        conversation: ConversationService | None = None,
        tts: PiperTTS | None = None,
    ) -> None:
        self.stt = stt or WhisperSTT()
        self.conversation = conversation or ConversationService()
        self.tts = tts or PiperTTS()

    def run_once(self, duration: float = 5) -> tuple[str, str, Path]:
        audio_path = record(duration)

        try:
            user_text = self.stt.transcribe(audio_path)
        finally:
            audio_path.unlink(missing_ok=True)

        answer = self.conversation.send(user_text)

        audio_path = self.tts.synthesize(answer)

        return user_text, answer, audio_path