from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from src.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean)
    points = relationship("Point", back_populates="users")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(String)
    long = Column(String)
    radcil = Column(String)
    radkon = Column(String)
    heightkon = Column(String)
    anglecon = Column(String)


class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    latpoint = Column(String)
    longpoint = Column(String)
    heightpoint = Column(String)
    user_id = Column(Integer, ForeignKey('users.id'))
    users = relationship("User", back_populates="points")
