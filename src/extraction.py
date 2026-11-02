import json
import os
from pathlib import Path

import requests
from dotenv import load_dotenv

from helpers.logger import logger

env_path = Path("/home/bruno/Projects/Python/etl-openweather-api/config/.env")
load_dotenv(env_path)

params = {
    "q": f"{os.getenv('CITY')},{os.getenv('COUNTRY')}",
    "units": os.getenv("UNIT", "metric"),
    "appid": os.getenv("API_KEY"),
}

url = "https://api.openweathermap.org/data/2.5/weather"

def extract_openweather_data(url: str) -> list:
    response = requests.get(url, params=params, timeout=10)
    data = response.json()

    if response.status_code != 200:
        logger.error(f"Erro na requisição. status code: {response.status_code}")
        return []

    if not data:
        logger.warning("Nenhum dado retornado")
        return []

    output_path = "data/raw/weather_data.json"
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"Arquivo salvo em: {output_path}")

    return data