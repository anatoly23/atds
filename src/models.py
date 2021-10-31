from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from src.database import Base
from math import tan, radians
from geographiclib.geodesic import Geodesic


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String)
    hashed_password = Column(String)
    disabled = Column(Boolean)
    pipes = relationship("Pipe", back_populates="users")


class Antenna(Base):
    __tablename__ = "antenas"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(Float)
    long = Column(Float)
    radcil = Column(Float)
    radkon = Column(Float)
    heightkon = Column(Float)
    anglecon = Column(Float)

    def if_overlap(self, point_lat: float, point_long: float, point_height: float) -> bool:
        geod = Geodesic.WGS84
        distance = geod.Inverse(point_lat, point_long, self.lat, self.long)
        if distance['s12'] < self.radkon:
            katet = tan(radians(self.anglecon)) * distance['s12']
            if katet + self.heightkon >= point_height:
                return False
            return True
        return False


class Pipe(Base):
    __tablename__ = "pipes"

    id = Column(Integer, primary_key=True, index=True)
    latpoint = Column(Float)
    longpoint = Column(Float)
    heightpoint = Column(Float)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship("User", back_populates="pipes")
