from pydantic import BaseModel
from typing import Optional


class AuthDetails(BaseModel):
    username: str
    password: str
    role: Optional[str] = None


class Item(BaseModel):
    lat: str
    long: str
    radcil: str
    radkon: str
    heightkon: str

    class Config:
        orm_mode = True
