import os
from loguru import logger
from dotenv import load_dotenv


logger.add(
    "info.log",
    format="{time} | {level} | {name}:{function}:{line} - {message}",
    filter=lambda record: record["level"].name in ["INFO", "SUCCESS"]
)

logger.add(
    "error.log",
    format="{time} | {level} | {name}:{function}:{line} - {message}",
    filter=lambda record: record["level"].name in ["ERROR", "CRITICAL", "WARNING"]
)

logger.add(
    "connect.log",
    format="{time} | {level} | {name}:{function}:{line} - {message}",
    filter=lambda record: 'Max retries exceeded with url' in record["message"]
)

# Загрузка переменных окружения из .env файла
load_dotenv()

# Доступ к переменным окружения
LOCAL_FOLDER_PATH = os.getenv('FOLDER_PATH')
CLOUD_FOLDER_PATH = os.getenv('CLOUD_FOLDER_PATH')
PERIOD = int(os.getenv('CHECK_PERIOD'))
TOKEN = os.getenv('TOKEN')
if not all((LOCAL_FOLDER_PATH, CLOUD_FOLDER_PATH, PERIOD, TOKEN)):
    raise Exception("Ошибка подгрузки данных из файла .env")