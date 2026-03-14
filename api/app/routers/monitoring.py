from fastapi import APIRouter , Depends
from typing import List
from app.schemas import LatestPosition, CollisionAlertSchema
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
            "ts": pos.ts
        })

    return result
  
  

@router.get("/collision-alerts", response_model=List[CollisionAlertSchema])
def get_collision_alerts(db: Session = Depends(get_db)):
    alerts = db.query(models.CollisionAlert).all()
    result = []

    for a in alerts:
        lat_a, lon_a, lat_b, lon_b = None, None, None, None

        if a.geom_a:
            point_a = wkb.loads(bytes.fromhex(a.geom_a))
            lon_a = point_a.x
            lat_a = point_a.y

        if a.geom_b:
            point_b = wkb.loads(bytes.fromhex(a.geom_b))
            lon_b = point_b.x
            lat_b = point_b.y

        result.append({
            "id": a.id,
            "created_at": a.created_at,
            "ts": a.ts,
            "mmsi_a": a.mmsi_a,
            "mmsi_b": a.mmsi_b,
            "dcpa_m": a.dcpa_m,
            "tcpa_s": a.tcpa_s,
            "latitude_a": lat_a,
            "longitude_a": lon_a,
            "latitude_b": lat_b,
            "longitude_b": lon_b,
            "sog_a": a.sog_a,
            "cog_a": a.cog_a,
            "sog_b": a.sog_b,
            "cog_b": a.cog_b,
            "severity": a.severity,
            "reason": a.reason,
            "details": a.details
        })

    return result