def test_settings_declares_all_required_fields():
    """All 9 required env vars must be declared as fields on Settings."""
    from app.core.config import Settings

    required_fields = {
        "DATABASE_URL",
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "BRAVE_API_KEY",
        "SENDGRID_API_KEY",
        "CLERK_SECRET_KEY",
        "NOTIFICATION_EMAIL",
        "FROM_EMAIL",
        "APP_URL",
    }
    declared = set(Settings.model_fields.keys())
    missing = required_fields - declared
    assert not missing, f"Settings is missing fields: {missing}"
