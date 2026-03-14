from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. database import get_db
from .. import models , schemas

router = APIRouter(prefix="/vessels" , tags = ["Vessels"])

@router.get("/" , response_model =list[schemas.Vessel])

def get_vessels(db: Session = Depends(get_db)):
    vessels = db.query(models.AISStatic).all()
    return vessels