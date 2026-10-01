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

def test_edit_transcript():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
    )

    controller.start_recording()
    controller.stop_recording()

    controller.edit_transcript("Poprawiona wiadomość.")

    assert controller.transcript == "Poprawiona wiadomość."


def test_send_uses_edited_transcript():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
    )

    controller.start_recording()
    controller.stop_recording()

    controller.edit_transcript("To jest poprawiona wiadomość.")

    answer = controller.send()

    assert answer == "Odpowiedź AI."
    assert conversation.sent_messages == ["To jest poprawiona wiadomość."]
    assert controller.state == ConversationState.IDLE


def test_send_is_not_possible_before_review():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
    )

    try:
        controller.send()
        assert False
    except RuntimeError:
        pass


class FakeTTS:
    def __init__(self) -> None:
        self.synthesized_texts = []

    def synthesize(self, text: str) -> Path:
        self.synthesized_texts.append(text)

        path = Path("/tmp/test-answer.wav")
        path.touch()

        return path


def test_send_generates_tts():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()
    tts = FakeTTS()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    controller.start_recording()
    controller.stop_recording()

    answer = controller.send()

    assert answer == "Odpowiedź AI."
    assert controller.audio_path == Path("/tmp/test-answer.wav")
    assert tts.synthesized_texts == ["Odpowiedź AI."]

    controller.audio_path.unlink(missing_ok=True)

def test_send_uses_edited_transcript_and_generates_tts():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()
    tts = FakeTTS()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    controller.start_recording()
    controller.stop_recording()

    controller.edit_transcript("To jest poprawiona wiadomość.")

    answer = controller.send()

    assert answer == "Odpowiedź AI."
    assert conversation.sent_messages == [
        "To jest poprawiona wiadomość."
    ]
    assert tts.synthesized_texts == ["Odpowiedź AI."]

    controller.audio_path.unlink(missing_ok=True)


def test_send_returns_to_idle_state():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()
    tts = FakeTTS()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
        tts=tts,
    )

    controller.start_recording()
    controller.stop_recording()

    answer = controller.send()

    assert answer == "Odpowiedź AI."
    assert controller.state == ConversationState.IDLE
    assert controller.answer == "Odpowiedź AI."
    assert controller.audio_path == Path("/tmp/test-answer.wav")

    controller.audio_path.unlink(missing_ok=True)

def test_can_record_again_from_review():
    recorder = FakeRecorder()
    stt = FakeSTT()
    conversation = FakeConversation()

    controller = ConversationController(
        recorder=recorder,
        stt=stt,
        conversation=conversation,
    )

    controller.start_recording()
    controller.stop_recording()

    assert controller.state == ConversationState.REVIEW

    controller.start_recording()

    assert controller.state == ConversationState.RECORDING
    assert controller.transcript is None
