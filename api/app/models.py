from sqlalchemy import Column, Integer, Float, String, DateTime , JSON , Boolean
from .database import Base
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class AISStatic(Base):
    __tablename__ = "ais_static"

    mmsi = Column(Integer, primary_key=True , index = True)
    shipname = Column(String)
    updated_at = Column(DateTime)
    last_raw_id = Column(Integer)
    extra = Column(JSON)


class AISPosition(Base):
    __tablename__ = "ais_positions"

    id = Column(Integer,primary_key=True, index=True)
    raw_id = Column(Integer)
    msg_type = Column(Integer)
    mmsi = Column(Integer)

    ts = Column(DateTime)
    station_id = Column(String)

    geom = Column(String)
    accuracy = Column(Boolean)
    sog = Column(Float)
    cog = Column(Float)
    heading= Column(Integer)
    nav_status =Column(Integer)
    rot = Column(Float)
    altitude = Column(Float)
    
    extra = Column(JSON)

class LatestPosition(Base):
    __tablename__ = "ais_latest_position"

    mmsi = Column(Integer , primary_key = True)
    ts = Column(DateTime)
    geom = Column(String)
    sog = Column(Float)
    cog = Column(Float)
    heading= Column(Integer)
    nav_status =Column(Integer)
    last_raw_id = Column(Integer)
    updated_at = Column(DateTime)
    
    
