import cartopy
from fastapi import FastAPI, File, UploadFile, Request, WebSocket, Form

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

from fastapi.templating import Jinja2Templates
import csv

from netCDF4 import Dataset
import cartopy.crs as ccrs


def raster_map(filename, output_filename):
    lon_min = -10
    lon_max = 180
    lat_min = 30
    lat_max = 80
    file_path = "static/" + filename  # Укажите имя файла, который хотите обработать
    print("file_path: ", file_path)
    with Dataset(file_path, "r") as nc:
        data = nc.variables["data"][:]
        # Создание растровой карты на фоне OpenStreetMap
        fig = plt.figure(figsize=(10, 6))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.imshow(data, extent=[lon_min, lon_max, lat_min, lat_max], origin='upper', cmap='viridis')
        ax.add_feature(cartopy.feature.OCEAN)
        ax.add_feature(cartopy.feature.LAND, edgecolor='black')
        ax.add_feature(cartopy.feature.COASTLINE)
        ax.add_feature(cartopy.feature.BORDERS, linestyle=':')
        ax.set_title("Raster Map")
        plt.savefig(output_filename)
    return {"message": "Raster map generated successfully"}


def raster_concat(filenames, output_filename):

    return {"message": "Raster map generated successfully"}
