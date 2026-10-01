from app.config import (
    DEEPSEEK_API_KEY,
    PIPER_MODEL,
    SAMPLE_RATE,
)


def test_sample_rate():
    assert SAMPLE_RATE == 48_000


def test_piper_model_exists():
    assert PIPER_MODEL.exists()


def test_deepseek_api_key_exists():
    assert DEEPSEEK_API_KEY
