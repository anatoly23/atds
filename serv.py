from typing import List
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Form, Response, Request
from fastapi.encoders import jsonable_encoder

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlalchemy.orm import Session
from src.schemas import AuthDetails, User, Item
from src.auth import get_current_active_user, get_password_hash, authenticate_user, users_db, create_access_token
from src import models, crud

import uvicorn

from src.database import SessionLocal, engine

ACCESS_TOKEN_EXPIRE_MINUTES = 30

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


templates = Jinja2Templates(directory="templates")

app = FastAPI()


@app.get('/', response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@app.post('/login', response_class=HTMLResponse)
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(users_db, username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)

    # response = RedirectResponse(url="/map")
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )

    return f'<p><a href="/map">Перейти на карту</a></p>'


@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response


@app.post('/register', status_code=201, response_class=HTMLResponse)
def register(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    data = {"username": username, "password": password, "role": role}
    auth_details = AuthDetails(**data)
    # if any(x['username'] == auth_details.username for x in users):
    if username in users_db:
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = get_password_hash(auth_details.password)
    users_db[auth_details.username] = {'username': auth_details.username, 'hashed_password': hashed_password}
    return f'<p><a href="/">На главную</a></p>'


@app.get('/map', response_class=HTMLResponse)
def get_map(request: Request, current_user: User = Depends(get_current_active_user)):
    return templates.TemplateResponse("map.html", context={"request": request})


# @app.post("/calc", response_model=Item)
# async def calc(item: Item, db: Session = Depends(get_db)):
#     return crud.create_item(db=db, item=item)


@app.get("/items", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db),
               current_user: User = Depends(get_current_active_user)):
    return crud.get_items(db, skip=skip, limit=limit)


@app.get('/protected', response_class=HTMLResponse)
def protected(current_user: User = Depends(get_current_active_user)):
    print(current_user)
    return f'Прувет!!!!'


if __name__ == "__main__":
    uvicorn.run("serv:app", host="127.0.0.1", port=8000, reload=True)
