from pydantic import BaseModel
from datetime import datetime


class Vessel(BaseModel):
  mmsi:int
  shipname :str |None
  updated_at: datetime |None

  class Config:
    from_attributes = True

class AISPositionSchema(BaseModel):
  mmsi:int
  ts: datetime
  station_id : str |None = None
  latitude:float |None
  longitude :float |None
  sog : float |None = None
  cog : float |None = None 

  class Config:
    from_attributes = True

class LatestPosition(BaseModel):
  mmsi: int 
  latitude:float |None
  longitude :float |None
  sog: float |None
  cog: float |None
  ts: datetime | None

  class Config:
    from_attributes = True

class CollisionAlertSchema(BaseModel):
    id: int
    created_at: datetime | None
    ts: datetime | None
    mmsi_a: int
    mmsi_b: int
    dcpa_m: float | None
    tcpa_s: float | None
    latitude_a: float | None
    longitude_a: float | None
    latitude_b: float | None
    longitude_b: float | None
    sog_a: float | None
    cog_a: float | None
    sog_b: float | None
    cog_b: float | None
    severity: str | None
    reason: str | None
    details: str | None

    class Config:
        from_attributes = True