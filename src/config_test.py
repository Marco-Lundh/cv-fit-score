import pytest

from src.config import get_settings


def test_settings_has_groq_api_key():
    assert isinstance(get_settings().groq_api_key, str)
    assert len(get_settings().groq_api_key) > 0


def test_settings_reads_from_env(monkeypatch):
    get_settings.cache_clear()
    monkeypatch.setenv("GROQ_API_KEY", "custom-test-key")
    assert get_settings().groq_api_key == "custom-test-key"
    get_settings.cache_clear()


def test_settings_raises_when_api_key_missing(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    from pydantic_settings import SettingsConfigDict
    from src.config import Settings

    class SettingsNoFile(Settings):
        model_config = SettingsConfigDict(env_file=None)

    with pytest.raises(ValueError, match="GROQ_API_KEY"):
        SettingsNoFile()
