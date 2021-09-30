from typing import Optional, List
from fastapi import FastAPI, Request, Form, HTTPException, Response, Cookie, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from src.auth import AuthHandler

from sqlalchemy.orm import Session
from src import crud, models, schemas
from src.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
templates = Jinja2Templates(directory="templates")

auth_handler = AuthHandler()
users = []


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get('/', response_class=HTMLResponse)
def index_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@app.post('/register', status_code=201, response_class=HTMLResponse)
def register(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    data = {"username": username, "password": password, "role": role}
    auth_details = schemas.AuthDetails(**data)
    if any(x['username'] == auth_details.username for x in users):
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = auth_handler.get_password_hash(auth_details.password)
    users.append({
        'username': auth_details.username,
        'password': hashed_password,
        'role': role
    })
    print(users)
    return f'Вы зарегистрированы!'


@app.post('/login', response_class=HTMLResponse)
def login(response: Response, username: str = Form(...), password: str = Form(...)):
    data = {"username": username, "password": password}
    auth_details = schemas.AuthDetails(**data)
    print(auth_details)
    user = None
    for x in users:
        if x['username'] == auth_details.username:
            user = x
            break

    if (user is None) or (not auth_handler.verify_password(auth_details.password, user['password'])):
        raise HTTPException(status_code=401, detail='Invalid username and/or password')
    token = auth_handler.encode_token(user['username'])
    response.set_cookie(
        key="authorization",
        value=token,
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return f'Добро пожаловать'


@app.get('/unprotected', response_class=HTMLResponse)
def unprotected(authorization: Optional[str] = Cookie(default=None)):
    print(type(authorization))
    if authorization:
        return f'cookie: {authorization}'
    return f'нет куки'


@app.get('/protected', response_class=HTMLResponse)
def protected(authorization: Optional[str] = Cookie(default=None)):
    auth_handler.decode_token(authorization)
    return f'Прувет!!!!'


@app.get('/delete', response_class=HTMLResponse)
def delete_cookie(responce: Response, authorization: Optional[str] = Cookie(default=None)):
    responce.delete_cookie(key="authorization")
    return f'Удалено'


@app.get('/map', response_class=HTMLResponse)
def get_map(request: Request):
    return templates.TemplateResponse("map.html", context={"request": request})


@app.post("/calc", response_model=schemas.Item)
async def calc(item: schemas.Item, db: Session = Depends(get_db)):
    return crud.create_item(db=db, item=item)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db, skip=skip, limit=limit)


if __name__ == "__main__":
    uvicorn.run("serv:app", host="127.0.0.1", port=8000, reload=True)
