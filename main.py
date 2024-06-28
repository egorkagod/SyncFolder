import time
from dotenv import load_dotenv
import os

# Загрузка переменных окружения из .env файла
load_dotenv()

# Доступ к переменным окружения
folder_path = os.getenv('FOLDER_PATH')
period = os.getenv('CHECK_PERIOD')
token = os.getenv('TOKEN')
if not all((folder_path, period, token)):
    raise Exception("Ошибка подгрузки данных из файла .env")


class Folder:
    """Класс Folder описывает папку операционной системы"""
    def __init__(self, path):
        # Проверка что путь ведет к папке
        if os.path.isdir(path):
            self.path = path
        else:
            raise Exception('Переданный путь приводит не к папке!')

    def is_exist(self):
        return os.path.exists(self.path)

    def get_files_list(self):
        return os.listdir(self.path)

    def start_logging(self, period=5):
        while True:
            print('Список файлов папки:', self.get_files_list())
            time.sleep(period)


MyFolder = Folder(folder_path)
MyFolder.start_logging()