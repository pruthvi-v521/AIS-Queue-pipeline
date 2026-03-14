from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models, schemas
from shapely import wkb

router = APIRouter(prefix="/positions")

@router.get("/" , response_model=list[schemas.AISPositionSchema])
def get_positions(db: Session = Depends(get_db)):
  positions = db.query(models.AISPosition).all()
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