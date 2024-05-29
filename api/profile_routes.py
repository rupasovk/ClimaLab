from fastapi import FastAPI, Request, Depends, HTTPException, APIRouter
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import database.crud
import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

profile_router = APIRouter(tags=["Profile"])
templates = Jinja2Templates(directory="templates")

SECRET_KEY = "your_super_secret_key"
ALGORITHM = "HS256"


# Функция, проверяющая авторизацию пользователя
async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Missing access token")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except (jwt.JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

    # Здесь вы должны реализовать логику получения информации о пользователе
    return {"username": username}


# Маршрут для страницы регистрации
@profile_router.get("/register", response_class=HTMLResponse)
def register(request: Request):
    return templates.TemplateResponse("user_register.html", {"request": request})


# Маршрут для страницы регистрации
@profile_router.get("/register/result", response_class=HTMLResponse)
def register(request: Request, username: str, password: str, confirm_password: str, email: str):
    message = ""
    print("////////////////////////////////////")
    print(username)
    print(password)
    print(email)
    print("////////////////////////////////////")

    try:
        hashed_password = password
        # hashed_password = get_password_hash(password)
        # if not verify_password(password, confirm_password):
        # raise "Пароли не совпадают!"

        database.crud.create_user(username, hashed_password, email)
        message = "User created successfully"
    except Exception as e:
        message = str(e)
        # raise HTTPException(status_code=500, detail=str(e))
    return templates.TemplateResponse("user_register_result.html", {"request": request, "reg_result": message})


# Маршрут для страницы авторизации
@profile_router.post("/login")
async def login(request: Request):
    # Здесь вы должны реализовать логику аутентификации пользователя
    # и возвращать токен доступа
    username = "example_user"
    password = "example_password"

    if username == "example_user" and password == "example_password":
        access_token = create_access_token(data={"sub": username})
        response = HTMLResponse(content="Logged in successfully!")
        response.set_cookie(key="access_token", value=access_token)
        return response
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Маршрут для страницы профиля пользователя
@profile_router.get("/profile", response_class=HTMLResponse)
async def profile(request: Request, user: dict = Depends(get_current_user)):
    return templates.TemplateResponse("profile.html", {"request": request, "user": user})


# Вспомогательная функция для создания JWT токена
def create_access_token(data: dict):
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)