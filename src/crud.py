from sqlalchemy.orm import Session
from src import models, schemas
from src.database import Session


def create_item(item: schemas.Item):
    db = Session()
    db_item = models.Item(lat=item.lat, long=item.long, radcil=item.radcil, radkon=item.radkon,
                          heightkon=item.heightkon, anglecon=item.anglecon)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item


def get_items(skip: int = 0, limit: int = 100):
    db = Session()
    items = db.query(models.Item).offset(skip).limit(limit).all()
    db.close()
    return items


def create_point(point: schemas.Point, user_id: int):
    db = Session()
    db_point = models.Point(latpoint=point.latpoint, longpoint=point.longpoint, heightpoint=point.heightpoint,
                            user_id=user_id)
    db.add(db_point)
    db.commit()
    db.refresh(db_point)
    db.close()
    return db_point


def get_points(user_id: int):
    db = Session()
    points = db.query(models.Point).filter(models.Point.user_id == user_id).all()
    db.close()
    return points


def create_user(user: schemas.UserInDB):
    db = Session()
    db_user = models.User(username=user.username, hashed_password=user.hashed_password, role=user.role, is_active=False)
    db.add(db_user)
    db.commit()
    db.close()
    return db_user


def get_user(username: str) -> schemas.UserInDB:
    db = Session()
    user = db.query(models.User).filter(models.User.username == username).first()
    db.close()
    return user
