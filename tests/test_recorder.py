from unittest.mock import patch

import numpy as np

from app.audio.recorder import record


@patch("app.audio.recorder.sd.wait")
@patch("app.audio.recorder.sd.rec")
def test_record(mock_rec, mock_wait):
    mock_rec.return_value = np.zeros((48_000, 1), dtype=np.int16)

    output_path = record(1)

    assert output_path.exists()
    assert output_path.suffix == ".wav"

    mock_rec.assert_called_once()
    mock_wait.assert_called_once()

    output_path.unlink()
