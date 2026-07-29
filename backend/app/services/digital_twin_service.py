import time
import math
from typing import Dict, Any, List


class DigitalTwinService:
    """
    Real-Time Digital Twin for Organ Transportation:
    Simulates Ambulance & Drone transport, GPS tracking, Cold Ischemia countdown,
    Temperature degradation curves, and Traffic-aware ETA prediction.
    """

    # Waypoints: Bengaluru Medical Corridor (Donor: Fortis Hospital -> Recipient: Apollo Hospital)
    WAYPOINTS = [
        {"lat": 12.8924, "lng": 77.5975, "name": "Fortis Hospital (Donor Site)"},
        {"lat": 12.9050, "lng": 77.5950, "name": "BG Road Flyover (Green Corridor)"},
        {"lat": 12.9220, "lng": 77.5920, "name": "Jayanagar 4th Block Intersection"},
        {"lat": 12.9400, "lng": 77.5880, "name": "Lalbagh West Gate Express Lane"},
        {"lat": 12.9580, "lng": 77.5850, "name": "Corporation Circle Priority Corridor"},
        {"lat": 12.9716, "lng": 77.5946, "name": "Apollo Specialty Hospital (Recipient ICU)"}
    ]

    _step_index = 0
    _historical_frames: List[Dict[str, Any]] = []

    @classmethod
    def get_live_twin_state(cls, mode: str = "ambulance") -> Dict[str, Any]:
        cls._step_index = (cls._step_index + 1) % len(cls.WAYPOINTS)
        wp = cls.WAYPOINTS[cls._step_index]

        # Calculate progress
        progress_pct = round((cls._step_index / (len(cls.WAYPOINTS) - 1)) * 100.0, 1)

        # Simulation dynamics
        base_speed = 72.0 if mode.lower() == "drone" else 54.0
        traffic_delay = 0.0 if mode.lower() == "drone" else (4.0 if cls._step_index in (2, 3) else 1.0)
        speed_kmh = round(base_speed - (traffic_delay * 3.0), 1)

        # Distance remaining
        remaining_waypoints = len(cls.WAYPOINTS) - 1 - cls._step_index
        remaining_distance_km = round(remaining_waypoints * 3.6, 2)

        # ETA Prediction vs Actual Research Comparison
        predicted_eta_minutes = int((remaining_distance_km / (base_speed / 60.0)) * 1.25)
        actual_eta_minutes = int(remaining_distance_km / (speed_kmh / 60.0)) if speed_kmh > 0 else 0

        # Cold Ischemia Timer Simulation (Max 6 hrs = 360 mins)
        elapsed_transport_minutes = cls._step_index * 7
        total_ischemia_limit_minutes = 360
        ischemia_remaining_minutes = max(0, total_ischemia_limit_minutes - elapsed_transport_minutes)

        # Temperature simulation (4.0°C base + subtle thermal flux)
        temp_celsius = round(4.0 + (cls._step_index * 0.15), 2)
        battery_level = round(100.0 - (cls._step_index * 1.5), 1)

        frame = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "mode": mode.upper(),
            "cold_box_id": "BOX-ESP32-001",
            "current_location": wp,
            "progress_percent": progress_pct,
            "speed_kmh": speed_kmh,
            "traffic_density": "LOW (Green Corridor Active)" if traffic_delay < 2.0 else "HEAVY TRAFFIC DELAY",
            "remaining_distance_km": remaining_distance_km,
            "predicted_eta_minutes": predicted_eta_minutes,
            "actual_eta_minutes": actual_eta_minutes,
            "eta_variance_minutes": abs(predicted_eta_minutes - actual_eta_minutes),
            "ischemia_remaining_minutes": ischemia_remaining_minutes,
            "ischemia_formatted": f"{ischemia_remaining_minutes // 60}h {ischemia_remaining_minutes % 60}m",
            "temperature_celsius": temp_celsius,
            "battery_percent": battery_level,
            "donor_hospital": cls.WAYPOINTS[0]["name"],
            "recipient_hospital": cls.WAYPOINTS[-1]["name"]
        }

        cls._historical_frames.append(frame)
        if len(cls._historical_frames) > 100:
            cls._historical_frames.pop(0)

        return frame

    @classmethod
    def get_historical_replay(cls) -> List[Dict[str, Any]]:
        return cls._historical_frames if cls._historical_frames else [cls.get_live_twin_state()]
