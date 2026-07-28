import datetime
from sqlalchemy import Column, Integer, DateTime
from backend.app.core.database import Base


class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
