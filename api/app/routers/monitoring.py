from fastapi import APIRouter , Depends
from typing import List
from app.schemas import LatestPosition
from ..database import get_db
from .. import models, schemas
from sqlalchemy.orm import Session
from shapely import wkb

router = APIRouter()

@router.get("/vessels/latest" , response_model = List[LatestPosition])
def get_latest_positions(db: Session = Depends(get_db)):
    latest_positions = db.query(models.LatestPosition).all()
    result = []

    for pos in latest_positions:
        lat, lon = None, None
        if pos.geom:
            # Convert WKB hex string to Point
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
            "ts": pos.ts , 
        })

    return result
  
  

