from unittest.mock import patch

import numpy as np

from app.audio.recorder import AudioRecorder


class FakeStream:
    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        pass


def test_recorder_start_stop():
    fake_stream = FakeStream()

    with patch(
        "app.audio.recorder.sd.InputStream",
        return_value=fake_stream,
    ):
        recorder = AudioRecorder()

        recorder.start()

        assert recorder.is_recording

        recorder._chunks = [
            np.zeros((48_000, 1), dtype=np.int16)
        ]

        output_path = recorder.stop()

    assert not recorder.is_recording
    assert output_path.exists()
    assert output_path.suffix == ".wav"
    assert output_path.stat().st_size > 0

    output_path.unlink()


def test_recorder_cannot_stop_before_start():
    recorder = AudioRecorder()

    try:
        recorder.stop()
        assert False
    except RuntimeError:
        pass


def test_recorder_cannot_start_twice():
    fake_stream = FakeStream()

    with patch(
        "app.audio.recorder.sd.InputStream",
        return_value=fake_stream,
    ):
        recorder = AudioRecorder()
        recorder.start()

        try:
            recorder.start()
            assert False
        except RuntimeError:
            pass

        recorder._chunks = [
            np.zeros((100, 1), dtype=np.int16)
        ]

        recorder.stop()