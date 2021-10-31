from datetime import timedelta
from typing import List

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Form, Response, Request, Security, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

import src.database
from src import crud
from src.auth import get_current_active_user, get_password_hash, authenticate_user, create_access_token
from src.schemas import Antenna, User, UserInDB, Pipe, Status, Token

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
    scopes = []
    if user.role == "operator":
        scopes = ['setantena', 'getantena']
    elif user.role == 'builder':
        scopes = ['setpipe', 'getpipe', 'getantena']
    access_token = create_access_token(
        data={"sub": user.username, "scopes": scopes}, expires_delta=access_token_expires
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


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "scopes": form_data.scopes}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.get('/map', response_class=HTMLResponse)
def get_map(request: Request, current_user: User = Depends(get_current_active_user)):
    return templates.TemplateResponse("map.html", context={"request": request, "role": current_user.role})


@app.post("/setantena", response_model=Antenna)
async def set_antena(antena: Antenna, current_user: User = Security(get_current_active_user, scopes=["setantena"])):
    return crud.create_antena(antena=antena)


@app.get("/getantena", response_model=List[Antenna])
def get_antena(skip: int = 0, limit: int = 100,
               current_user: User = Security(get_current_active_user, scopes=["getantena"])):
    return crud.get_antena(skip=skip, limit=limit)


@app.post("/setpipe", response_model=Status)
def set_pipe(pipe: Pipe, skip: int = 0, limit: int = 100,
             current_user: User = Security(get_current_active_user, scopes=["setpipe"])):
    antenas = crud.get_antena(skip=skip, limit=limit)
    for antena in antenas:
        if antena.if_overlap(pipe.latpoint, pipe.longpoint, pipe.heightpoint):
            return {"status": False}

    crud.create_pipe(pipe=pipe, user_id=current_user.id)
    return {"status": True}


@app.get("/getpipe", response_model=List[Pipe])
def get_pipe(current_user: User = Security(get_current_active_user, scopes=["getpipe"])):
    points = crud.get_pipe(user_id=current_user.id)
    return points


if __name__ == "__main__":
    uvicorn.run("serv:app", host="127.0.0.1", port=8000, reload=True)
