from fastapi import APIRouter, Depends, HTTPException, Request
from typing import List
from sqlalchemy.orm import Session
from starlette import status

from fastapi.templating import Jinja2Templates
from database.crud import get_db
from database.models import User
from database.crud import create_user, update_user, delete_user, read_users
from fastapi.responses import HTMLResponse, RedirectResponse

user_router = APIRouter(
    # prefix="/users",
    tags=["Users"],
    # responses={404: {"description": "Not found"}},
)

templates = Jinja2Templates(directory="templates")


@user_router.get("/users", response_model=None)
def get_users(request: Request):
    users = read_users()
    print(users)
    return templates.TemplateResponse("users.html", {"request": request, "users": users, "nav_param": "users"})


@user_router.post("/users", response_model=None, status_code=status.HTTP_201_CREATED)
def create_user(name: str, password: str, mail: str):
    user = create_user(name=name, password=password, mail=mail)
    return user


@user_router.get("/users/{user_id}", response_model=None)
def get_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@user_router.put("/users/edit/{user_id}", response_model=None)
def update_user(user_id: int, user: update_user, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.username = user.username
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    return db_user


@user_router.delete("/users/delete/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
