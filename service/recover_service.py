import numpy as np
from pykrige.ok import OrdinaryKriging
import pandas as pd
from tqdm import tqdm
import seaborn as sns
from numpy.core.numeric import NaN
from sklearn.impute import KNNImputer
import statsmodels.api as sm
from numpy.core.numeric import NaN
import matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.linear_model import LinearRegression


def test_recover(input_filename, input_filename_sep, station_filename, station_filename_sep, output_filename, data_type, model_type):
    stations = pd.read_csv(station_filename, sep=station_filename_sep)
    clean_data = pd.read_csv(input_filename, sep=input_filename_sep)

    # Создание словаря для отображения старых и новых имен столбцов
    columns_mapping = {
        'Year': 'year',
        'Jan': 'jan',
        'Feb': 'feb',
        'March': 'mar',
        'April': 'apr',
        'May': 'may',
        'June': 'jun',
        'July': 'jul',
        'August': 'aug',
        'September': 'sep',
        'October': 'oct',
        'November': 'nov',
        'December': 'dec',
        'Annual': 'per_year',
        'Station_Number': 'station_number',
        'x': 'lon',
        'y': 'lat',
        'Type_data': 'data_type',
    }

    # Переименование столбцов с использованием метода rename()
    clean_data_renamed = clean_data.rename(columns=columns_mapping)

    # print(clean_data)

    # Объединение таблиц
    joined_data = clean_data_renamed.merge(stations, left_on='station_number', right_on='Index')

    clean_data_temperature = joined_data[joined_data["data_type"] == "Av_Temp"]  # .head(500) # Данные без пропусков температура
    clean_data_precip = joined_data[joined_data["data_type"] == "Sum_Precip"]  # .head(500) # Данные без пропусков осадки

    if data_type == "temperature":
        data = clean_data_temperature.dropna().copy()  # Вызвать для анализа температуры
    else:
        data = clean_data_precip.dropna().copy()  # Вызвать для анализа сумм осадков

    df = pd.DataFrame(data)

    # Создание копии DataFrame с пропусками-------------------------------------------
    df_with_missing = df.copy()

    # Доля пропущенных значений (например, 20%)
    missing_ratio = 0.05

    # Определение столбцов, в которых будут созданы пропуски
    columns_with_missing = ['jan', 'feb', 'mar', 'apr']

    # Генерация случайных индексов для пропусков
    num_missing = int(np.round(df_with_missing[columns_with_missing].size * missing_ratio))
    missing_indices = np.random.choice(df_with_missing.index, num_missing, replace=False)

    # Установка значений NaN по случайным индексам
    df_with_missing.loc[missing_indices, columns_with_missing] = np.nan

    # Вывод DataFrame со случайными пропусками
    # print(df_with_missing)
    # Создание копии DataFrame с пропусками-------------------------------------------

    # Создание копии DataFrame с пропусками для восстановления
    df_missing = df_with_missing.copy()

    if model_type == "kriging":
        # Восстановление пропущенных значений кригингом
        imputed_df = mean_recover(df_missing, 5)
    elif model_type == "regression":
        # Восстановление пропущенных значений регрессией
        imputed_df = regression_recover(df_missing)
    else:
        # Восстановление пропущенных значений усреднением
        imputed_df = mean_recover(df_missing, 5)
    # Вычисление коэффициента регрессии и p-value
    regression_results = mean_recover1(imputed_df)

    # Вывод результатов
    # print("Исходный DataFrame:")
    # print(df)
    # print("\nВосстановленный DataFrame:")
    # print(imputed_df)
    # print("\nРезультаты линейной регрессии:")

    # for station, coefficient, p_value in regression_results:
    #     print(f"Станция {station}: Коэффициент = {coefficient}, p-value = {p_value}")

    # Вычисляем ошибки
    mae = mean_absolute_error(imputed_df[['jan', 'feb', 'mar', 'apr']], df[['jan', 'feb', 'mar', 'apr']])
    mape = np.mean(np.abs((imputed_df[['jan', 'feb', 'mar', 'apr']] - df[['jan', 'feb', 'mar', 'apr']]) / df[['jan', 'feb', 'mar', 'apr']])) * 100
    rmse = np.sqrt(mean_squared_error(imputed_df[['jan', 'feb', 'mar', 'apr']], df[['jan', 'feb', 'mar', 'apr']]))
    std_dev = np.std(imputed_df[['jan', 'feb', 'mar', 'apr']])

    # Вывод результатов
    print("MAE:", mae)
    print("MAPE:", mape)
    print("RMSE:", rmse)
    print("Стандартное отклонение:", std_dev)
    # print(regression_results)
    regression_results_df = pd.DataFrame(regression_results)
    regression_results_df.columns = ["station", "coef", "p-value"]

    print(type(std_dev))
    print(std_dev)
    # errors_results_df = pd.DataFrame(std_dev)
    # errors_results_df.columns = ["std_dev"]
    # Преобразование в pd.DataFrame
    std_dev_df = std_dev.to_frame().reset_index().rename(columns={"index": "month"})
    std_dev_df.columns = ["month", "std_dev"]

    errors_results_df = [mae, mape, rmse, std_dev_df]
    print(type(errors_results_df))
    print(errors_results_df)

    return df_missing, imputed_df, regression_results_df, errors_results_df


def mean_recover2(df, k):
    results = df.copy()
    for station in df['station_number'].unique():
        station_df = df[df['station_number'] == station]
        x = station_df['year']
        y = station_df[['jan', 'feb', 'mar', 'apr']]
        y = y.mean(axis=1)  # Усреднение значений по месяцам
    return results


def mean_recover(df, k):
    imputed_df = df.copy()
    cols = ['jan', 'feb', 'mar', 'apr']
    # Группируем данные по году и месяцу
    grouped = imputed_df.groupby(['year'])
    # Применяем усреднение к пропущенным значениям в каждой группе
    imputer = KNNImputer(n_neighbors=k)
    imputed_values = imputer.fit_transform(imputed_df[cols])

    # Заменяем пропущенные значения в DataFrame
    imputed_df.loc[:, cols] = imputed_values

    return imputed_df


# Запустить восстановление пропусков с использованием усреднения значений за тот же год в определенном радиусе
def mean_recover1(df):
    results = []
    for station in df['station_number'].unique():
        station_df = df[df['station_number'] == station]
        x = station_df['year']
        y = station_df[['jan', 'feb', 'mar', 'apr']]
        y = y.mean(axis=1) # Усреднение значений по месяцам
        x = sm.add_constant(x) # Добавление константы для модели
        model = sm.OLS(y, x).fit() # Линейная регрессия
        if len(model.params) > 1 and len(model.pvalues) > 1:
          #print((station, model.params[1], model.pvalues[1]))
          results.append((station, model.params[1], model.pvalues[1]))
    return results


# Восстановление пропусков с использованием усреднения значений за тот же год в определенном радиусе
def mean_imputation(df):
    imputed_df = df.copy()
    imputer = KNNImputer(n_neighbors=5)
    print(imputer)
    # cols = ['jan', 'feb', 'mar', 'apr']
    # imputed_df[cols] = imputer.fit_transform(imputed_df[cols])
    return imputer


def regression_recover(df_with_missing):
    # Уникальные значения номеров станций
    station_numbers = df_with_missing['station_number'].unique()
    # station_numbers = df[(df['station_number'] != 28678) & (df['station_number'] != 28679) & (df['station_number'] != 28713) & (df['station_number'] != 28776) & (df['station_number'] != 28807) & (df['station_number'] != 28902) & (df['station_number'] != 28903)]['station_number'].unique()

    # Применяем восстановление пропущенных значений для каждой станции и каждого столбца (jan, feb, mar, apr)
    for station_number in station_numbers:
        print(f"[[{station_number}]]")
        tmp_output_df = df_with_missing[df_with_missing['station_number'] == station_number]
        for column in ['jan', 'feb', 'mar', 'apr']:
            tmp_output_df[column], coefficients, p_values = linear_regression_imputation(df_with_missing, station_number, column)
            tmp_output_df['coefficient'] = [coefficients] * len(tmp_output_df)
            tmp_output_df['p-value'] = [p_values] * len(tmp_output_df)
            # print(f"{column} коэффициенты регрессии:", coefficients)
            # print(f"{column} p-value:", p_values)
        output_df = output_df.append(tmp_output_df)
    return output_df


# Функция для восстановления пропущенных значений линейной регрессией в зависимости от года
def linear_regression_imputation(df, station_number, column):
    df_imputed = df.copy()
    df_imputed_station = df_imputed[df_imputed['station_number'] == station_number]
    X = df_imputed_station[df_imputed_station[column].notnull()]['year'].values.reshape(-1, 1)
    y = df_imputed_station[df_imputed_station[column].notnull()][column].values
    X = sm.add_constant(X)  # Добавляем константный признак
    model = sm.OLS(y, X)  # Создаем модель OLS
    results = model.fit()  # Обучаем модель
    X_pred = df_imputed_station[df_imputed_station[column].isnull()]['year'].values.reshape(-1, 1)
    X_pred = sm.add_constant(X_pred)  # Добавляем константный признак и к X_pred
    y_pred = results.predict(X_pred)  # Предсказываем значения

    # Присваиваем предсказанные значения каждому пропущенному элементу
    df_imputed_station.loc[df_imputed_station[column].isnull(), column] = y_pred

    return df_imputed_station[column], results.params[1:], results.pvalues[1:]
