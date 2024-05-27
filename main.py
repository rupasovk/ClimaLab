import cartopy
from fastapi import FastAPI, File, UploadFile, Request, WebSocket, Form
#ddd
from fastapi.staticfiles import StaticFiles
import os
from service import netcdf_service as ncs

from fastapi.templating import Jinja2Templates
import csv

from fastapi import FastAPI


from api.main_routes import main_router
from api.file_processing_routes import file_processing_router
from api.cleaning_routes import cleaning_router
from api.parsing_routes import parsing_router
from api.gaps_filling_routes import gaps_filling_router

#from database import database
#from model.User import User
#from model.Role import Role
import uuid

from netCDF4 import Dataset

app = FastAPI()

app.include_router(main_router)
app.include_router(file_processing_router)
app.include_router(cleaning_router)
app.include_router(parsing_router)
app.include_router(gaps_filling_router)

templates = Jinja2Templates(directory="templates")

# Подключаем статические файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

directory_name = "static/"
service_views_directory_name = "service_views/"
file_views_directory_name = "file_views/"

# Глобальная переменная с поддерживаемыми расширениями файлов для просмотра
viewable_extensions = ["csv", "pdf", "jpg", "jpeg", "png", "gif"]



# NetCDF обработка-------------------------------------------------------

@app.get("/start-process-channel")
def index(request: Request):
    return templates.TemplateResponse("netcdf_views/netcdf_page.html", {"request": request})


@app.get("/process-channel")
def process_channel(channel_name: str):
    # Обработка выбранного канала
    # channel_name - имя выбранного канала

    # Открываем NetCDF файл
    nc_file = Dataset("static/mean_tas_may_june_data.nc", "r")

    print(nc_file)
    # Получаем данные выбранного канала
    channel_data = nc_file.variables[channel_name][:]

    # Закрываем NetCDF файл
    nc_file.close()

    return channel_data.tolist()


@app.get("/netcdf_page")
async def netcdf_page(request: Request):
    # Отображение страницы netcdf
    return templates.TemplateResponse("netcdf_views/netcdf_cropping_page.html", {"request": request})


@app.get("/netcdf_map")
async def raster_map(request: Request, open_filename: str):
    print(open_filename)
    ncs.raster_map(open_filename, "static/netcdf/raster_map.png")
    return templates.TemplateResponse("netcdf_views/netcdf_cropping_page.html", {"request": request})


@app.get("/netcdf_concat")
async def raster_map(request: Request, concat_files: str, concat_files_sep: str, output_filename: str):
    ncs.raster_concat(concat_files.split(concat_files_sep), output_filename)
    return templates.TemplateResponse("netcdf_views/netcdf_cropping_page.html", {"request": request})


@app.get("/available-channels")
def available_channels():
    # Открываем NetCDF файл
    nc_file = Dataset("static/mean_tas_may_june_data.nc", "r")

    # Получаем список доступных каналов
    channels = nc_file.variables.keys()
    print(channels)

    # Закрываем NetCDF файл
    nc_file.close()

    return list(channels)


from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import xarray as xr
import matplotlib.pyplot as plt
from PIL import Image
import io


@app.get("/start-process-file")
def index(request: Request):
    return templates.TemplateResponse("netcdf_views/netcdf_index.html", {"request": request})


def generate_plot(variable, lat, lon):
    # Создаем график с использованием Cartopy
    fig = plt.figure(figsize=(10, 6))
    ax = plt.axes()

    # Отображаем растр
    ax.imshow(variable, cmap='jet', origin='upper', extent=[lon.min(), lon.max(), lat.min(), lat.max()])

    # Добавляем шкалу цветов
    #plt.colorbar(label='Value')

    # Настраиваем отображение графика
    ax.set_title('NetCDF Raster')
    ax.set_xlabel('Lon')
    ax.set_ylabel('Lat')

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return buf


@app.post("/process-file")
async def process_file(file: UploadFile = File(...)):
    # Открываем NetCDF-файл
    dataset = xr.open_dataset("static/mean_tas_may_june_data.nc")

    # Извлекаем переменную с растром
    variable = dataset['tas'].isel(year=0)  # Извлекаем первый временной шаг

    # Извлекаем координаты широты и долготы
    lat = dataset['lat']
    lon = dataset['lon']

    # Преобразуем переменную в массив NumPy и изменяем форму
    variable_np = variable.values

    # Генерируем график растра
    plot_buf = generate_plot(variable_np, lat, lon)

    # Создаем объект PIL Image из буфера
    image = Image.open(plot_buf)

    print(lat, lon)

    # Возвращаем изображение в виде HTML-страницы
    return HTMLResponse(content=image_to_html(image), media_type="text/html")


def image_to_html(image):
    # Преобразуем изображение в HTML-строку
    buf = io.BytesIO()
    image.save(buf, format='PNG')
    data = buf.getvalue()
    #encoded = data.encode('base64').replace('\n', '')
    html = f'<img src="data:image/png;base64,{data}">'
    return html


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)