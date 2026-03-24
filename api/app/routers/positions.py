from fastapi import APIRouter, Depends , Query
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from shapely import wkb
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/positions")

@router.get("/" , response_model=list[schemas.AISPositionSchema])

def get_positions(mmsi : int , 
                start : Optional[datetime]=Query(None , descripton = "Start datetime"),
                end: Optional[datetime] = Query(None, description="End datetime"), 
                db: Session = Depends(get_db)):
  
  
  query = db.query(models.AISPosition).filter(models.AISPosition.mmsi == mmsi)
  if start:
    query = query.filter(models.AISPosition.ts >= start)

  if end:
    query = query.filter(models.AISPosition.ts <= end)

  positions = query.order_by(models.AISPosition.ts.asc()).all()
#   positions = db.query(models.AISPosition).all()
  result = []

  for pos in positions:

      lat, lon = None, None

      if pos.geom:
          wkb_bytes = bytes.fromhex(pos.geom)
          point = wkb.loads(wkb_bytes)
          lon = point.x
          lat = point.y

      result.append({
            "mmsi": pos.mmsi,
            "latitude": lat,
            "longitude": lon,
            "sog": pos.sog,
            "cog": pos.cog,
            "ts": pos.ts
        })

  return result