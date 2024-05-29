from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile, Request, WebSocket, Form
from service import parsing_service as ps
from fastapi.templating import Jinja2Templates
import config

parsing_router = APIRouter(tags=["Parsing"])
templates = Jinja2Templates(directory="templates")


@parsing_router.get("/parse")
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
    return templates.TemplateResponse(config.service_views_directory_name + "parsing.html", {"request": request})

