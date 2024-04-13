import cartopy
from fastapi import FastAPI, File, UploadFile, Request, WebSocket, Form
#ddd
from fastapi.staticfiles import StaticFiles
from matplotlib import pyplot as plt
from starlette.responses import FileResponse
import os
import pandas as pd
from pydantic import BaseModel
from fastapi.responses import HTMLResponse, RedirectResponse

from service import parsing_service as ps
from service import cleaning_service as cs
from service import recover_service as rs
from service import netcdf_service as ncs

from fastapi.templating import Jinja2Templates
import csv

from netCDF4 import Dataset
import cartopy.crs as ccrs

app = FastAPI()
templates = Jinja2Templates(directory="templates")


# Определение функции-фильтра splitext
def splitext(value):
    # print(value)
    # print(os.path.splitext(value)[1][1:].lower())
    return os.path.splitext(value)[1][1:].lower()


# Регистрация функции-фильтра splitext в Jinja2
templates.env.filters['splitext'] = splitext


# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

directory_name = "static/"
service_views_directory_name = "service_views/"
file_views_directory_name = "file_views/"

# Глобальная переменная с поддерживаемыми расширениями файлов для просмотра
viewable_extensions = ["csv", "pdf", "jpg", "jpeg", "png", "gif"]

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("main.html", {"request": request, "nav_param": "main"})


@app.get("/parsing")
async def parsing(request: Request):
    return templates.TemplateResponse(service_views_directory_name + "parsing.html", {"request": request, "nav_param": "parsing"})


@app.get("/file_management1")
async def files(request: Request):
    static_dir = "static"
    files = os.listdir(static_dir)

    return templates.TemplateResponse("file_management.html", {"request": request, "files": files})


@app.get("/about")
async def files(request: Request):
    return templates.TemplateResponse("about.html", {"request": request, "nav_param": "about"})


@app.get("/page1")
async def index1(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("page1.html", {"request": request, "files": files, "viewable_extensions": viewable_extensions})


@app.post("/upload2")
async def upload_file(file: UploadFile = File(...)):
    """
    Обрабатывает загруженный файл и сохраняет его на сервере
    """
    with open(f"static/{file.filename}", "wb") as f:
        contents = await file.read()
        f.write(contents)
    return {"filename": file.filename}


@app.get("/download/{filename}")
async def download_file(filename: str):
    """
    Позволяет пользователю скачать файл с сервера
    """
    return FileResponse(f"static/{filename}", filename=filename)


@app.post("/delete1")
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
@app.get("/file_management")
async def index(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("file_management.html", {"request": request, "files": files, "viewable_extensions": viewable_extensions, "nav_param": "file"})


@app.post("/file_management")
async def index(request: Request):
    files = os.listdir("static")
    return templates.TemplateResponse("file_management.html", {"request": request, "files": files, "nav_param": "file"})


@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    file_path = os.path.join("static", file.filename)
    with open(file_path, "wb") as f:
        f.write(contents)

    # Перенаправление обратно на страницу со списком файлов
    return RedirectResponse(url="file_management")


class DeleteRequest(BaseModel):
    filename: str


@app.post("/delete")
async def delete_file(request: DeleteRequest):
    filename = request.filename
    file_path = os.path.join("static", filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"message": "File deleted"}
    else:
        return {"message": "File not found"}


@app.get("/view/{filename}")
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


@app.get("/files")
def file_list(request: Request):
    directory = 'static/'  # Укажите путь к директории
    files = os.listdir(directory)
    return templates.TemplateResponse("file_list.html", {"request": request, "files": files})


@app.get("/parse")
async def start_parsing_weather_climate(request: Request, filename: str, separator: str, output_filename: str):
    """
    Позволяет получить данные с портала "Погода и климат" для указанных метеостанций
    """
    # directory_name = "static/"
    # stations_sep = ';'

    # station_ids = pd.read_csv(directory_name + filename, sep=stations_sep)
    # station_ids = pd.read_csv('/content/list_of_station_id.csv', sep=';', error_bad_lines=False)
    # station_ids = station_ids['Index'].values
    # print(station_ids)

    ps.start_parsing(filename, separator, output_filename)
    return templates.TemplateResponse(service_views_directory_name + "parsing.html", {"request": request})


@app.get("/cleaning_page")
async def cleaning_page(request: Request):
    return templates.TemplateResponse("cleaning_data.html", {"request": request, "nav_param": "cleaning"})


@app.get("/cleaning")
async def start_cleaning(request: Request, filename: str, min_error_bound: int, max_error_bound: int, output_filename: str):
    # Чистка данных
    cs.cleaning_data(directory_name + filename, min_error_bound, max_error_bound, directory_name + output_filename)
    return templates.TemplateResponse("cleaning_data.html", {"request": request, "nav_param": "cleaning"})


@app.get("/recover1")
async def process_form(request: Request):
    form_data = await request.form()
    print(form_data)
    button_value = form_data["button"]
    print(button_value)
    if button_value == "real":
        return RedirectResponse("/recover_start")
    elif button_value == "test":
        return RedirectResponse("/recover_test")


@app.get("/recover_page")
async def recover_page(request: Request):
    # Отображение страницы с графиком
    return templates.TemplateResponse("recover_service_view/recover_data.html", {"request": request, "nav_param": "recover"})


@app.get("/recover")
def recover_data(request: Request, stations_filename: str, stations_filename_sep: str, data_filename: str, data_filename_sep: str, output_filename: str, data_type: str, model_type: str, button: str):
    print(stations_filename)
    print(stations_filename_sep)
    print(data_filename)
    print(data_filename_sep)
    print(output_filename)
    print(data_type)
    print(model_type)

    if button == "real":
        # Обработка нажатия кнопки "Запустить восстановление"
        return RedirectResponse(f"/recover_start?stations_filename={stations_filename}&stations_filename_sep={stations_filename_sep}&data_filename={data_filename}&data_filename_sep={data_filename_sep}&output_filename={output_filename}&data_type={data_type}&model_type={model_type}")
    elif button == "test":
        # Обработка нажатия кнопки "Тест выбранной модели"
        return RedirectResponse(f"/recover_test?stations_filename={stations_filename}&stations_filename_sep={stations_filename_sep}&data_filename={data_filename}&data_filename_sep={data_filename_sep}&output_filename={output_filename}&data_type={data_type}&model_type={model_type}")


@app.get("/recover_start")
async def recover_start(request: Request, filename: str, filename_sep: str, output_filename: str, output_filename_sep: str, data_type: str, model_type: str):
    # Создание данных для графика
    recover_data = []

    data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}
    df = pd.DataFrame(data)

    # Создание графика
    plt.plot(df['x'], df['y'])
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('График Pandas')

    # Сохранение графика в файл
    plt.savefig('static/graph.png')
    plt.close()

    # Отображение страницы с результатами восстановления
    return templates.TemplateResponse("recover_service_view/recover_result.html", {"request": request, "filename": filename, "recover_data": recover_data})


@app.get("/recover_test")
async def recover_test(request: Request, stations_filename: str, stations_filename_sep: str, data_filename: str, data_filename_sep: str, output_filename: str, data_type: str, model_type: str):
    # Создание данных для графика

    data = {'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}
    df = pd.DataFrame(data)

    # Создание графика
    plt.plot(df['x'], df['y'])
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('График Pandas')

    # Сохранение графика в файл
    plt.savefig('static/graph.png')
    plt.close()

    missing_data, recover_data, regression_results, errors = rs.test_recover(directory_name + data_filename, data_filename_sep, directory_name + stations_filename, stations_filename_sep, output_filename, data_type, model_type)

    # print("missing_data", missing_data)
    # print("recover_data", recover_data)
    # print("regression_results", regression_results)
    # print("errors")
    # print("MAE: ", errors[0])
    # print("MAPE: ", errors[1])
    # print("RMSE: ", errors[2])
    # print("STD: ", errors[3])

    # Отображение страницы с результатами восстановления
    return templates.TemplateResponse("recover_service_view/recover_test_result.html", {"request": request, "filename": data_filename, "model_type": model_type, "missing_data": missing_data, "recover_data": recover_data, "regression_results": regression_results, "errors": errors})


# NetCDF обработка-------------------------------------------------------
@app.get("/netcdf_page")
async def netcdf_page(request: Request):
    # Отображение страницы netcdf
    return templates.TemplateResponse("netcdf_views/netcdf_page.html", {"request": request})


@app.get("/netcdf_map")
async def raster_map(request: Request, open_filename: str):
    print(open_filename)
    ncs.raster_map(open_filename, "static/netcdf/raster_map.png")
    return templates.TemplateResponse("netcdf_views/netcdf_page.html", {"request": request})


@app.get("/netcdf_concat")
async def raster_map(request: Request, concat_files: str, concat_files_sep: str, output_filename: str):
    ncs.raster_concat(concat_files.split(concat_files_sep), output_filename)
    return templates.TemplateResponse("netcdf_views/netcdf_page.html", {"request": request})
