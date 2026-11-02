import os
import pandas as pd
from dotenv import load_dotenv

from helpers.logger import logger
from sqlalchemy import  create_engine, text
from urllib.parse import quote_plus
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / "config" / ".env"
load_dotenv(env_path)

user = os.getenv("DB_USER")
passwd = os.getenv("DB_PASSWORD")
database = os.getenv("DATABASE")

host = "host.docker.internal"

def get_engine():
    logger.info(f"Conectando em: {host}:5432/{database}")
    return  create_engine(
        f"postgresql+psycopg2://{user}:{quote_plus(passwd)}@{host}:5432/{database}"
    )

engine = get_engine()

def load_data(table_name: str, df: pd.DataFrame):
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists="append",
        index=False
    )

    df_check = pd.read_sql(f"SELECT * FFROM {table_name}", con=engine)
    logger.info(f"Total de registos na tabela: {len(df_check)}\n")