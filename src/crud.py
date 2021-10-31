from sqlalchemy.orm import Session

from src import models, schemas
from src.database import Session


def create_antena(antena: schemas.Antenna):
    db = Session()
    db_item = models.Antenna(lat=antena.lat, long=antena.long, radcil=antena.radcil, radkon=antena.radkon,
                             heightkon=antena.heightkon, anglecon=antena.anglecon)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


def get_antena(skip: int = 0, limit: int = 100) -> schemas.Antenna:
    db = Session()
    items = db.query(models.Antenna).offset(skip).limit(limit).all()
    db.close()
    return items


def create_pipe(pipe: schemas.Pipe, user_id: int):
    db = Session()
    db_point = models.Pipe(latpoint=pipe.latpoint, longpoint=pipe.longpoint, heightpoint=pipe.heightpoint,
                           user_id=user_id)
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    db.close()
    return db_point


def get_pipe(user_id: int):
    db = Session()
    points = db.query(models.Pipe).filter(models.Pipe.user_id == user_id).all()
    db.close()
    return points


def create_user(user: schemas.UserInDB):
    db = Session()
    db_user = models.User(username=user.username, hashed_password=user.hashed_password, role=user.role, disabled=False)
    db.add(db_user)
    db.commit()
    db.close()
    return db_user


def get_user(username: str) -> schemas.UserInDB:
    db = Session()
    user = db.query(models.User).filter(models.User.username == username).first()
    db.close()
    return user
