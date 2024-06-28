import time
from dotenv import load_dotenv
import os
import json
import requests


# Загрузка переменных окружения из .env файла
load_dotenv()

# Доступ к переменным окружения
folder_path = os.getenv('FOLDER_PATH')
period = os.getenv('CHECK_PERIOD')
token = os.getenv('TOKEN')
if not all((folder_path, period, token)):
    raise Exception("Ошибка подгрузки данных из файла .env")

# Описывание заголовком запроса к YandexDisk
headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': f'OAuth {token}'
    }


class Folder:
    """Класс Folder описывает папку операционной системы"""
    def __init__(self, path):
        # Проверка что путь ведет к папке
        if os.path.isdir(path):
            self.path = path
        else:
            raise Exception('Переданный путь приводит не к папке!')

    def get_files_list(self):
        files = []
        for filename in os.listdir(self.path):
            file = {
                'name': filename,
                'path': self.path + f'{filename}/'
            }
            files.append(file)
        return files

    def start_logging(self, period=5):
        while True:
            print('Список файлов папки:', self.get_filenames_list())
            time.sleep(period)


class CloudFolder:
    main_url = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, headers):
        self.headers = headers

    def get_files_list(self):
        url = self.main_url + 'resources/'
        params = {
            'path': 'disk:/Applications/Yandex Polygon/SyncFolder/',
            'fields': 'name, _embedded.items.path,_embedded.items.name, _embedded.items.type'
        }
        response = requests.get(url, headers=headers, params=params)
        print(response.status_code)
        print(json.dumps(response.json()["_embedded"]["items"], indent=4))

    def upload_file(self, file_path):
        directory, filename = os.path.split(file_path)
        url = self.main_url + 'resources/upload/'
        params = {
            'path': f'disk:/Applications/Yandex Polygon/SyncFolder/{filename}',
        }
        upload_url = requests.get(url, headers=self.headers, params=params)
        if upload_url:
            with open(file_path, 'rb') as file:
                upload_response = requests.put(upload_url["href"], data=file)
                if upload_response.status_code == 201:
                    print('Файл успешно загружен!')
                else:
                    print(f'Файл не загрузился с ошибкой {upload_response.status_code}')
                    print(upload_response.text)
        else:
            print(f'Upload url не был получен с ошибкой {upload_url.status_code}')
            print(upload_url.text)


Folder = Folder(folder_path)
YFolder = CloudFolder(headers)
YFolder.upload_file('C:/Users/pirat/OneDrive/Рабочий стол/SyncFolder/TextFile.txt/')
YFolder.get_files_list()