from pathlib import Path

from app.conversation.controller import (
    ConversationController,
    ConversationState,
)


class FakeRecorder:
    def __init__(self) -> None:
        self.started = False
        self.stopped = False

    def start(self) -> None:
        self.started = True

    def stop(self) -> Path:
        self.stopped = True

        path = Path("/tmp/test-recording.wav")
        path.touch()

        return path


class FakeSTT:
    def transcribe(self, audio_path: Path) -> str:
        return "To jest testowa transkrypcja."


class FakeConversation:
    def __init__(self) -> None:
        self.sent_messages = []

    def send(self, message: str) -> str:
        self.sent_messages.append(message)
        return "Odpowiedź AI."


def test_recording_flow_stops_at_review():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
    )

    assert controller.state == ConversationState.IDLE

    controller.start_recording()

    assert controller.state == ConversationState.RECORDING
    assert recorder.started

    transcript = controller.stop_recording()

    assert transcript == "To jest testowa transkrypcja."
    assert controller.transcript == "To jest testowa transkrypcja."
    assert controller.state == ConversationState.REVIEW

    # Najważniejsze:
    # transkrypcja nie została jeszcze wysłana do LLM.
    assert conversation.sent_messages == []


def test_cannot_start_recording_twice():
    controller = ConversationController(
        recorder=FakeRecorder(),
        stt=FakeSTT(),
        conversation=FakeConversation(),
    )

    controller.start_recording()

    try:
        controller.start_recording()
        assert False
    except RuntimeError:
        pass


def test_cannot_stop_when_not_recording():
    controller = ConversationController(
        recorder=FakeRecorder(),
        stt=FakeSTT(),
        conversation=FakeConversation(),
    )

    try:
        controller.stop_recording()
        assert False
    except RuntimeError:
        pass
