from typing import List, Optional
from sqlalchemy.orm import Session
from backend.app.models.domain import GPSLocation, Transport


class TelemetryRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_telemetry_reading(
        self,
        cold_box_id: str,
        lat: float,
        lng: float,
        temp_celsius: float,
        humidity_percent: float,
        battery_level: float,
        transport_id: Optional[int] = None
    ) -> GPSLocation:
        reading = GPSLocation(
            cold_box_id=cold_box_id,
            lat=lat,
            lng=lng,
            temp_celsius=temp_celsius,
            humidity_percent=humidity_percent,
            battery_level=battery_level,
            transport_id=transport_id
        )
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def get_latest_telemetry(self, cold_box_id: str) -> Optional[GPSLocation]:
        return (
            self.db.query(GPSLocation)
            .filter(GPSLocation.cold_box_id == cold_box_id)
            .order_by(GPSLocation.timestamp.desc())
            .first()
        )

    def get_telemetry_history(self, cold_box_id: str, limit: int = 50) -> List[GPSLocation]:
        return (
            self.db.query(GPSLocation)
            .filter(GPSLocation.cold_box_id == cold_box_id)
            .order_by(GPSLocation.timestamp.desc())
            .limit(limit)
            .all()
        )
