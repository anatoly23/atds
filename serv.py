from typing import List
from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, Form, Response, Request
from fastapi.encoders import jsonable_encoder

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

from src.schemas import Item, User, UserInDB, Point, Status
from src.auth import get_current_active_user, get_password_hash, authenticate_user, create_access_token
# optimize import
from src import crud
import src.database
from src.checkoverlap import if_overlap

import uvicorn

ACCESS_TOKEN_EXPIRE_MINUTES = 30

src.database.create_db()

templates = Jinja2Templates(directory="templates")

app = FastAPI()


@app.get('/', response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("login.html", context={"request": request})


@app.post('/login', response_class=HTMLResponse)
async def login(username: str = Form(...), password: str = Form(...)):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": username}, expires_delta=access_token_expires
    )

    token = jsonable_encoder(access_token)
    response: Response = RedirectResponse('/map', status_code=303)
    response.set_cookie(
        "Authorization",
        value=f"Bearer {token}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response


@app.get("/logout")
async def route_logout_and_remove_cookie():
    response = RedirectResponse(url="/")
    response.delete_cookie("Authorization")
    return response


@app.post('/register', status_code=201, response_class=HTMLResponse)
def register(username: str = Form(...), password: str = Form(...), role: str = Form(...)):
    data = {"username": username, "password": password, "role": role, "disabled": False}
    auth_details = User(**data)
    user_in_bd = crud.get_user(username)
    if user_in_bd:
        raise HTTPException(status_code=400, detail='Username is taken')
    hashed_password = get_password_hash(auth_details.password)
    userdata = {"username": username, "hashed_password": hashed_password, "role": role,
                "disabled": auth_details.disabled}
    user = UserInDB(**userdata)
    crud.create_user(user)
    return RedirectResponse(url="/", status_code=303)


@app.get('/map', response_class=HTMLResponse)
def get_map(request: Request, current_user: User = Depends(get_current_active_user)):
    return templates.TemplateResponse("map.html", context={"request": request})


@app.post("/set", response_model=Item)
async def calc(item: Item, current_user: User = Depends(get_current_active_user)):
    return crud.create_item(item=item)


@app.get("/items", response_model=List[Item])
def read_items(skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user)):
    return crud.get_items(skip=skip, limit=limit)


@app.post("/setpoint", response_model=Status)
def set_point(point: Point, skip: int = 0, limit: int = 100, current_user: User = Depends(get_current_active_user)):
    radio_objects = crud.get_items(skip=skip, limit=limit)
    for object in radio_objects:
        if if_overlap(float(point.latpoint), float(point.longpoint), float(point.heightpoint), float(object.lat),
                      float(object.long), float(object.radkon), float(object.anglecon), float(object.heightkon)):
            return {"status": False}

    crud.create_point(point=point, user_id=current_user.id)
    return {"status": True}


@app.get("/getpoint", response_model=List[Point])
def get_point(current_user: User = Depends(get_current_active_user)):
    points = crud.get_points(user_id=current_user.id)
    return points


if __name__ == "__main__":
    uvicorn.run("serv:app", host="127.0.0.1", port=8000, reload=True)
