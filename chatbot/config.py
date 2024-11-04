from os import environ
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")


class Config:
    """Класс с переменными окружения"""

    QA_HOST: str = environ.get("QA_HOST", default="")
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@{environ.get('POSTGRES_HOST')}/{environ.get('POSTGRES_DB')}"
    )
    TG_ACCESS_TOKEN: str = environ.get("TG_ACCESS_TOKEN", default="")
