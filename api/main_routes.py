from fastapi import APIRouter
import cartopy
from fastapi import FastAPI, File, UploadFile, Request
import os
from fastapi.templating import Jinja2Templates
import config

main_router = APIRouter(tags=["Main"])

templates = Jinja2Templates(directory="templates")


@main_router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "nav_param": "main"})

#@main_router.get("/users")
#async def home(request: Request):
#    # Пример использования модели User
#    new_user = User(id=uuid.uuid4(), name='John Doe')
#    database.session.add(new_user)
#    database.session.commit()

#    return templates.TemplateResponse("main.html", {"request": request, "nav_param": "main"})


#@main_router.get("/roles")
#async def home(request: Request):
#    # Пример использования модели Roles
#    new_role = Role(id=uuid.uuid4(), name='Admin')
#    database.session.add(new_role)
#    database.session.commit()


#    return templates.TemplateResponse("main.html", {"request": request, "nav_param": "main"})


@main_router.get("/parsing")
async def parsing(request: Request):
    return templates.TemplateResponse(config.service_views_directory_name + "parsing.html", {"request": request, "nav_param": "parsing"})


@main_router.get("/file_management1")
async def files(request: Request):
    static_dir = "static"
    files = os.listdir(static_dir)

    return templates.TemplateResponse("file_management.html", {"request": request, "files": files})


@main_router.get("/about")
async def files(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "nav_param": "about"})


# @main_router.get("/users")
# async def files(request: Request):
#    return templates.TemplateResponse("users.html", {"request": request, "nav_param": "users"})
