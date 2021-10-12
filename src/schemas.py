from pydantic import BaseModel
from typing import Optional, List


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

    class Config:
        orm_mode = True


class Status(BaseModel):
    status: bool
