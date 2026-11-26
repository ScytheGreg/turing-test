from app.config import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    DEEPSEEK_MODEL,
)


def test_deepseek_configuration_exists():
    assert DEEPSEEK_API_URL.startswith("https://")
    assert DEEPSEEK_MODEL


def test_deepseek_api_key_exists():
    assert DEEPSEEK_API_KEY
