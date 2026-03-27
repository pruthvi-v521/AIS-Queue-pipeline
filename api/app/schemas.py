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



    