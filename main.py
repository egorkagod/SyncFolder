import time
from dotenv import load_dotenv
import os
import json
import requests


# Загрузка переменных окружения из .env файла
load_dotenv()

# Доступ к переменным окружения
local_folder_path = os.getenv('FOLDER_PATH')
cloud_folder_path = os.getenv('CLOUD_FOLDER_PATH')
period = os.getenv('CHECK_PERIOD')
token = os.getenv('TOKEN')
if not all((local_folder_path, cloud_folder_path, period, token)):
    raise Exception("Ошибка подгрузки данных из файла .env")

def create_local_path(filename):
    return os.path.join(local_folder_path, filename)

def create_remote_path(filename):
    return f'{cloud_folder_path}/{filename}'

class Folder:
    """Описывает папку операционной системы"""
    def __init__(self, path):
        # Проверка что путь ведет к папке
        if os.path.isdir(path):
            self.path = path
        else:
            raise Exception('Переданный путь приводит не к папке!')

    def get_files_list(self):
        files = {}
        for filename in os.listdir(self.path):
            files[filename] = create_local_path(filename)
        return files

    def start_logging(self, period=5):
        file_set = set(self.get_files_list())
        while True:
            print('Текущие файлы в папке:')
            for filename in file_set:
                print('\t', filename)
            time.sleep(period)
            check_set = set(self.get_files_list())
            add_set = {}; remove_set = {}
            if file_set != check_set:
                add_set = check_set - file_set
                remove_set = file_set - check_set
            for filename in add_set:
                print(f'Добавился новый файл {filename}')
            for filename in remove_set:
                print(f'Удалили файл {filename}')
            file_set = check_set

    def sync(self):
        pass


class CloudFolder:
    """Описывает папку на облачном сервисе"""
    main_url = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, path, token):
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token}'
        }
        self.path = path
        self.headers = headers

    def get_files_list(self):
        """
        Получает список файлов на облаке в виде списка из словарей
        """
        url = self.main_url + 'resources/'
        params = {
            'path': f'{self.path}',
            'fields': 'name, _embedded.items.path,_embedded.items.name, _embedded.items.type'
        }
        response = requests.get(url, headers=self.headers, params=params)
        print(response.status_code)
        print(json.dumps(response.json()["_embedded"]["items"], indent=4))

    def upload_file(self, filename):
        """
        Загружает файл на облако

        :param filename: имя файла
        """
        url = self.main_url + 'resources/upload/'
        params = {
            'path': f'{create_remote_path(filename)}',
            'overwrite': 'true',
        }
        upload_url = requests.get(url, headers=self.headers, params=params)
        if upload_url:
            with open(create_local_path(filename), 'rb') as file:
                upload_response = requests.put(upload_url.json()["href"], data=file)
                if upload_response.status_code == 201:
                    print('Файл успешно загружен!')
                else:
                    print(f'Файл не загрузился с ошибкой {upload_response.status_code}')
                    print(upload_response.text)
        else:
            print(f'Upload url не был получен с ошибкой {upload_url.status_code}')
            print(upload_url.text)

    def delete_file(self, filename):
        """
            Удаляет файл с облака

            :param filename: имя файла
        """
        url = self.main_url + 'resources/'
        params = {
            'path': f'{create_remote_path(filename)}',
            'permanently': 'true',
        }
        delete_response = requests.delete(url, headers=self.headers, params=params)
        if delete_response.status_code == 204:
            print('Файл успешно удален!')
        else:
            print(f'Файл не смог удалится с ошибкой {delete_response.status_code}')
            print(delete_response.text)


Folder = Folder(local_folder_path)
Folder.start_logging()
# YFolder = CloudFolder(cloud_folder_path, token)
# YFolder.delete_file('Hello World.txt')
# YFolder.upload_file('C:/Users/pirat/Desktop/SyncFolder/Document.docx')
# YFolder.get_files_list()