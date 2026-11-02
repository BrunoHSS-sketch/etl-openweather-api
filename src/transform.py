from __future__ import annotations

import json
import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from helpers.logger import logger

env_path = Path("/home/bruno/Projects/Python/etl-openweather-api/config/.env")
load_dotenv(env_path)

path_save_dataframe = Path(__file__).parent.parent / "data" / "validated"
path_name = Path(__file__).parent.parent / "data" / "raw" / "weather_data.json"
columns_name_to_drop = ["weather","weather_icon"]
columns_name_to_rename = {
    "base": "base",
    "visibility": "visibility",
    "dt": "datetime",
    "timezone": "timezone",
    "id": "city_id",
    "name": "city_name",
    "cod": "code",
    "coord.lon": "longitude",
    "coord.lat": "latitude",
    "main.temp": "temperatura",
    "main.feels_like": "feels_like",
    "main.temp_min": "temp_min",
    "main.temp_max": "temp_max",
    "main_pressure": "pressure",
    "main.humidity": "humidity",
    "main.sea_level": "sea_level",
    "main.grnd_level": "grnd_level",
    "wind.speed": "wind_speed",
    "wind.deg": "wind_deg",
    "wind.gust": "wind_gust",
    "clouds.all": "clouds",
    "sys.id": "sys_id",
    "sys_country": "country",
    "sys.sunrise": "sunrise",
    "sys.sunset": "sunset"
}
columns_normalize_datetime = ["datetime", "sunrise", "sunset"]

def create_dataframe(path_name: str | Path) -> pd.DataFrame:
    logger.info("Criando o DataFrame com base no json")

    path = Path(path_name)

    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    df = pd.json_normalize(data)
    logger.info("DataFrame criado com sucesso!")

    return df

def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("Inicializando a normalização")
    df_weather = pd.json_normalize(df['weather'].apply(lambda x: x[0]))

    df_weather = df_weather.rename(columns={
        "id": "weather_id",
        "main": "weather_main",
        "desciption": "weather_description",
        "icon": "weather_icon"
    })

    df = pd.concat([df,df_weather], axis=1)
    logger.info("DataFrame normalizado")

    return df

def drop_columns(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:
    logger.info(f"Removendo colunas: {columns_name}")
    
    df = df.drop(columns=columns_name)

    logger.info("Colunas removidas")
    return df

def rename_columns(df: pd.DataFrame, columns_name: dict[str,str]) -> pd.DataFrame:
    logger.info(f"Renomeando as colunas: {columns_name}")
    df = df.rename(columns=columns_name)
    logger.info("Renomeada as colunas")
    return df

def normalize_datetime_column(df: pd.DataFrame, columns_name: list[str]) -> pd.DataFrame:
    logger.info(f"Convertendo as colunas para Datetime: {columns_name}")
    for name in columns_name:
        tz = os.getenv("UTC") or "UTC"
        df[name] = (
            pd.to_datetime(df[name], unit="s", utc=True).dt.tz_convert(tz)
        )
    logger.info("Colunas convertidas para Datetime")
    return df

def save_dataframe(df: pd.DataFrame, path_save_dataframe: str | Path) -> None: 
    logger.info("Salvando o arquivo em formato parquet")
    path = Path(path_save_dataframe)
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / "weather.parquet"
    df.to_parquet(file_path)
    logger.info("Arquivo salvo com sucesso")


def data_transformation() -> None:
    logger.info("Inicializando a transformação")
    df = create_dataframe(path_name)
    df = normalize_dataframe(df)
    df = drop_columns(df, columns_name_to_drop)
    df = rename_columns(df, columns_name_to_rename)
    df = normalize_datetime_column(df, columns_normalize_datetime)
    save_dataframe(df, path_save_dataframe)
    logger.success("Transformação concluída com sucesso!")

data_transformation()