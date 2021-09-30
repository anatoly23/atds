from sqlalchemy import Column, String, Integer

from .database import Base


# class User(Base):
#     __tablename__ = "users"
#
#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True)
#     hashed_password = Column(String)
#     is_active = Column(Boolean, default=True)
#
#     items = relationship("Item", back_populates="owner")


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    lat = Column(String, index=True)
    long = Column(String, index=True)
    radcil = Column(String, index=True)
    radkon = Column(String, index=True)
    heightkon = Column(String, index=True)
