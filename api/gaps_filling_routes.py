from fastapi import APIRouter
from fastapi import FastAPI, File, UploadFile, Request, WebSocket, Form
from matplotlib import pyplot as plt
import pandas as pd
from fastapi.responses import HTMLResponse, RedirectResponse
from service import recover_service as rs
from fastapi.templating import Jinja2Templates
import config

gaps_filling_router = APIRouter()

templates = Jinja2Templates(directory="templates")


@gaps_filling_router.get("/recover1")
async def process_form(request: Request):
    form_data = await request.form()
    print(form_data)
    button_value = form_data["button"]
    print(button_value)
    if button_value == "real":
        return RedirectResponse("/recover_start")
    elif button_value == "test":
        return RedirectResponse("/recover_test")


@gaps_filling_router.get("/recover_page")
async def recover_page(request: Request):
    # Отображение страницы с графиком
    return templates.TemplateResponse("recover_service_view/recover_data.html", {"request": request, "nav_param": "recover"})


@gaps_filling_router.get("/recover")
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


@gaps_filling_router.get("/recover_start")
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


@gaps_filling_router.get("/recover_test")
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

    missing_data, recover_data, regression_results, errors = rs.test_recover(config.directory_name + data_filename, data_filename_sep, config.directory_name + stations_filename, stations_filename_sep, output_filename, data_type, model_type)

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
