from fastapi import APIRouter, FastAPI, File, UploadFile, Request, WebSocket, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from starlette.responses import FileResponse
from pydantic import BaseModel

import csv
import pandas as pd
import os


file_processing_router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Глобальная переменная с поддерживаемыми расширениями файлов для просмотра
viewable_extensions = ["csv", "pdf", "jpg", "jpeg", "png", "gif"]


# Определение функции-фильтра splitext
def splitext(value):
    # print(value)
    # print(os.path.splitext(value)[1][1:].lower())
    return os.path.splitext(value)[1][1:].lower()


# Регистрация функции-фильтра splitext в Jinja2
templates.env.filters['splitext'] = splitext


directory_name = "static/"
service_views_directory_name = "service_views/"
file_views_directory_name = "file_views/"


@file_processing_router.get("/page1")
async def index1(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("page1.html", {"request": request, "files": files, "viewable_extensions": viewable_extensions})


@file_processing_router.post("/upload2")
async def upload_file(file: UploadFile = File(...)):
    """
    Обрабатывает загруженный файл и сохраняет его на сервере
    """
    with open(f"static/{file.filename}", "wb") as f:
        contents = await file.read()
        f.write(contents)
    return {"filename": file.filename}


@file_processing_router.get("/download/{filename}")
async def download_file(filename: str):
    """
    Позволяет пользователю скачать файл с сервера
    """
    return FileResponse(f"static/{filename}", filename=filename)


@file_processing_router.post("/delete1")
async def delete_file(request: Request):
    form = await request.form()
    filename = form["filename"]
    directory = 'static/'  # Укажите путь к директории
    filepath = os.path.join(directory, filename)

    if os.path.isfile(filepath):
        os.remove(filepath)
        message = f"Файл '{filename}' успешно удален."
    else:
        message = f"Файл '{filename}' не найден."

    files = os.listdir("static")
    return templates.TemplateResponse("page1.html", {"request": request, "files": files})


# ///REGION FILE MANAGEMENT////////////////////////////////////////////////////////////////////
@file_processing_router.get("/file_management")
async def index(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("file_management.html", {"request": request, "files": files, "viewable_extensions": viewable_extensions, "nav_param": "file"})


@file_processing_router.post("/file_management")
async def index(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("file_management.html", {"request": request, "files": files, "nav_param": "file"})


@file_processing_router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_path = os.path.join("static", file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Перенаправление обратно на страницу со списком файлов
    return RedirectResponse(url="file_management")


class DeleteRequest(BaseModel):
    filename: str


@file_processing_router.post("/delete")
async def delete_file(request: DeleteRequest):
    filename = request.filename
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "File deleted"}
    else:
        return {"message": "File not found"}


@file_processing_router.get("/view/{filename}")
async def view_file(request: Request, filename: str):
    # Определение расширения файла
    file_extension = filename.split(".")[-1].lower()

    # Определение представления файла в зависимости от расширения
    if file_extension == "pdf":
        # Логика для открытия PDF-файла
        # pdf_url = request.url_for("get_pdf", filename=filename)
        pdf_path = f"static/{filename}"
        return FileResponse(pdf_path, media_type="application/pdf")
        # return templates.TemplateResponse("pdf_view.html", {"request": request, "pdf_url": pdf_url})

    elif file_extension == "csv":
        # Путь к файлу в папке static
        file_path = f"{directory_name + filename}"

        # Чтение данных из файла
        csv_data = []
        csv_data_describe = []
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                # print(row)
                # row_list = row.split(";")
                csv_data.append(row)

        # Преобразование в DataFrame
        df = pd.DataFrame(csv_data[1:], columns=csv_data[0])
        # print(df.dropna().std())
        # csv_data_describe = df.describe()

        return templates.TemplateResponse(file_views_directory_name + "csv_view.html", {"request": request, "csv_data": csv_data, "csv_data_describe": csv_data_describe, "tmp_title": "Просмотр csv файла: " + filename})

    elif file_extension in ["png", "jpg", "jpeg", "gif"]:
        # Логика для открытия картинки
        # image_url = request.url_for("get_image", filename=filename)
        image_path = f"{filename}"
        return templates.TemplateResponse(file_views_directory_name + "image_view.html", {"request": request, "image_path": image_path, "tmp_title": "Просмотр image файла: " + filename})
# /////END//////////////////////////////////////////////////////////////////


@file_processing_router.get("/files")
def file_list(request: Request):
    directory = 'static/'  # Укажите путь к директории
    files = os.listdir(directory)
    return templates.TemplateResponse("file_list.html", {"request": request, "files": files})
