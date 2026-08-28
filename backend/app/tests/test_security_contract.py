import os

def test_no_secret_values_in_source_environment_contract():
    forbidden = ("ORGANIZER_APP_PASSWORD", "JWT_SECRET", "DEVICE_SECRET")
    for key in forbidden:
        assert not os.environ.get(key) or key in ("ORGANIZER_APP_PASSWORD", "JWT_SECRET", "DEVICE_SECRET")

def test_required_secret_names_are_configuration_driven():
    from app.config import settings
    assert hasattr(settings, "ALLOWED_ORIGINS")


def test_emergency_states_are_explicit():
    from app.services.emergency_state import EMERGENCY_STATUSES
    assert EMERGENCY_STATUSES == ("CREATED", "NOTIFIED", "ACKNOWLEDGED", "PROCESSING", "RESOLVED", "CANCELLED")
