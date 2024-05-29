from fastapi import APIRouter
import cartopy
from fastapi import FastAPI, File, UploadFile, Request
import os
from fastapi.templating import Jinja2Templates
from service import cleaning_service as cs
import config


cleaning_router = APIRouter(tags=["Cleaning"])

templates = Jinja2Templates(directory="templates")


#directory_name = "static/"
#service_views_directory_name = "service_views/"
#file_views_directory_name = "file_views/"


@cleaning_router.get("/cleaning_page")
async def cleaning_page(request: Request):
    return templates.TemplateResponse("cleaning_data.html", {"request": request, "nav_param": "cleaning"})


@cleaning_router.get("/cleaning")
async def start_cleaning(request: Request, filename: str, min_error_bound: int, max_error_bound: int, output_filename: str):
    # Чистка данных
    cs.cleaning_data(config.directory_name + filename, min_error_bound, max_error_bound, config.directory_name + output_filename)
    return templates.TemplateResponse("cleaning_data.html", {"request": request, "nav_param": "cleaning"})

