from src.config import Settings


def test_settings_has_groq_api_key():
    from src.config import settings
    assert isinstance(settings.groq_api_key, str)
    assert len(settings.groq_api_key) > 0


def test_settings_reads_from_env(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "custom-test-key")
    fresh = Settings()
    assert fresh.groq_api_key == "custom-test-key"
