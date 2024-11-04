from os import environ
from dotenv import load_dotenv

load_dotenv(dotenv_path="../.env")


class Config:
    """Класс с переменными окружения"""

    YANDEX_API_KEY: str = environ.get("YANDEX_API_KEY", default="")
    YANDEX_FOLDER_ID: str = environ.get("YANDEX_FOLDER_ID", default="")
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql://{environ.get('POSTGRES_USER')}:{environ.get('POSTGRES_PASSWORD')}@{environ.get('POSTGRES_HOST')}/{environ.get('POSTGRES_DB')}"
    )
    TEXT_SOURCE_URL: str = environ.get("TEXT_SOURCE_URL", default="")
