from os import environ
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path=dotenv_path)

class Config:
    """Класс, содержащий переменные окружения."""

    YANDEX_API_KEY: str = environ.get("YANDEX_API_KEY", default="")
    YANDEX_FOLDER_ID: str = environ.get("YANDEX_FOLDER_ID", default="")
    TEXT_SOURCE_URL: str = environ.get("TEXT_SOURCE_URL", default="")