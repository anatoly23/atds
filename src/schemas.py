from pydantic import BaseModel
from typing import Optional, List

from math import tan, radians
from geographiclib.geodesic import Geodesic


class Point(BaseModel):
    latpoint: str
    longpoint: str
    heightpoint: str

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
    scopes: List[str] = []


class User(BaseModel):
    username: str
    password: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None
    points: List[Point] = []

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class Item(BaseModel):
    lat: str
    long: str
    radcil: str
    radkon: str
    heightkon: str
    anglecon: str

    @staticmethod
    def if_overlap(point_lat: float, point_long: float, point_height: float, lat: float, long: float, radkon: float,
                   angelcon: float, heightkon: float) -> bool:
        geod = Geodesic.WGS84
        distance = geod.Inverse(point_lat, point_long, lat, long)
        if distance['s12'] < radkon:
            katet = tan(radians(angelcon)) * distance['s12']
            if katet + heightkon >= point_height:
                return False
            return True
        return False

    class Config:
        orm_mode = True


class Status(BaseModel):
    status: bool
