from typing import Optional, List

from pydantic import BaseModel


class Pipe(BaseModel):
    latpoint: float
    longpoint: float
    heightpoint: float

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str = None
    scopes: List[str] = []


class User(BaseModel):
    id: Optional[int]
    username: str
    password: Optional[str] = None
    role: Optional[str] = None
    disabled: Optional[bool] = None
    points: List[Pipe] = []

    class Config:
        orm_mode = True


class UserInDB(User):
    hashed_password: str


class Antenna(BaseModel):
    lat: float
    long: float
    radcil: float
    radkon: float
    heightkon: float
    anglecon: float

    class Config:
        orm_mode = True


class Status(BaseModel):
    status: bool
