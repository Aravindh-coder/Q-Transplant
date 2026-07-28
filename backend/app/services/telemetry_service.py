from typing import Tuple, Dict
from backend.app.core.logging import logger


class TelemetryService:
    SAFE_TEMP_MIN = 2.0
    SAFE_TEMP_MAX = 8.0

    @classmethod
    def evaluate_cold_box(cls, temp_celsius: float, battery_level: float) -> Tuple[bool, str]:
        """Evaluates whether temperature or battery is in alert state."""
        warnings = []
        is_alarm = False

        if temp_celsius < cls.SAFE_TEMP_MIN:
            warnings.append(f"FREEZE WARNING: Temp {temp_celsius}°C below safe minimum ({cls.SAFE_TEMP_MIN}°C)")
            is_alarm = True
        elif temp_celsius > cls.SAFE_TEMP_MAX:
            warnings.append(f"ISCHEMIA ALERT: Temp {temp_celsius}°C exceeds safe threshold ({cls.SAFE_TEMP_MAX}°C)")
            is_alarm = True

        if battery_level < 15.0:
            warnings.append(f"LOW BATTERY: Cold box power at {battery_level}%")
            is_alarm = True

        if is_alarm:
            msg = " | ".join(warnings)
            logger.warning(f"[TELEMETRY ALARM] {msg}")
            return True, msg

        return False, "Nominal operational status"
