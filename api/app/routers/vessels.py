from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. database import get_db
from .. import models , schemas
from typing import Optional
from fastapi import Query

router = APIRouter(prefix="/vessels" , tags = ["Vessels"])

@router.get("/" , response_model =list[schemas.Vessel])

def get_vessels( name: Optional[str] = Query(None, description="Filter by vessel name"),
    limit: int = Query(100, ge=1, le=500, description="Limit number of results"),
    sort_by: str = Query("updated_at",
    description="Sort field"),db: Session = Depends(get_db)):

    query = db.query(models.AISStatic)

    if name:
        query = query.filter(models.AISStatic.shipname.ilike(f"%{name}%"))

    if sort_by == "updated_at":
        query = query.order_by(models.AISStatic.updated_at.desc())

    query = query.limit(limit)

    return query.all()

    # vessels = db.query(models.AISStatic).all()
    # return vessels