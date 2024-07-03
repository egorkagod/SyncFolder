import datetime
import time
from dotenv import load_dotenv
import os
import requests
from loguru import logger
from datetime import datetime


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
local_folder_path = os.getenv('FOLDER_PATH')
cloud_folder_path = os.getenv('CLOUD_FOLDER_PATH')
period = int(os.getenv('CHECK_PERIOD'))
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
        if os.path.isdir(path):
            self.path = path
        else:
            raise Exception('Переданный путь из .env приводит не к папке!')

    def get_files_list(self):
        files = {}
        for filename in os.listdir(self.path):
            path = create_local_path(filename)
            files[filename] = {'name': filename, 'path': path, 'modified': datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()}
        return files

    def download_file(self, filename, CloudFolder):
        url = CloudFolder.main_url + 'resources/download/'
        params = {
            'path': f'{create_remote_path(filename)}',
        }
        download_url = CloudFolder.connect(url, headers=CloudFolder.headers, params=params)
        if download_url:
            url = download_url.json()["href"]
            with open(create_local_path(filename), 'wb') as file:
                download_response = CloudFolder.connect(url)
                file.write(download_response.content)
                logger.success(f'Файл {filename} успешно скачан с облака!')

    def first_sync_modifications(self, CloudFolder):
        local_files = self.get_files_list()
        cloud_files = CloudFolder.get_files_list()
        intersection = set(local_files) & set(cloud_files)
        for filename in intersection:
            if cloud_files[filename]['modified'] > local_files[filename]['modified']:
                Folder.download_file(filename, CloudFolder)
            elif cloud_files[filename]['modified'] < local_files[filename]['modified']:
                CloudFolder.upload_file(filename)

    def first_sync_by_name(self, CloudFolder):
        file_set = set(self.get_files_list())
        cloud_set = set(CloudFolder.get_files_list())
        add_to_local = cloud_set - file_set
        add_to_cloud = file_set - cloud_set
        for filename in add_to_local:
            self.download_file(filename, CloudFolder)
        for filename in add_to_cloud:
            CloudFolder.upload_file(filename)

    def first_sync(self, CloudFolder):
        self.first_sync_modifications(CloudFolder)
        self.first_sync_by_name(CloudFolder)
        logger.success('Первичная синхронизация прошла успешно!')

    def start_logging(self, CloudFolder, period=period):
        self.first_sync(CloudFolder)
        while True:
            files_before = self.get_files_list()
            time.sleep(period)
            self.logging_files(files_before, CloudFolder)

    def logging_files_by_names(self, files_before, CloudFolder):
        files_now = set(self.get_files_list())
        add_set = files_now - files_before
        remove_set = files_before - files_now
        for filename in add_set:
            CloudFolder.upload_file(filename)
        for filename in remove_set:
            CloudFolder.delete_file(filename)

    def logging_files(self, files_before, CloudFolder):
        files_now = self.get_files_list()
        intersection = set(files_before) & set(files_now)
        for filename in intersection:
            if files_now[filename]['modified'] > files_before[filename]['modified']:
                CloudFolder.upload_file(filename)
        self.logging_files_by_names(set(files_before), CloudFolder)


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

    def connect(self, url, headers=None, params=None, data=None, method='GET'):
        while True:
            try:
                response = requests.request(method, url, headers=headers, params=params, data=data, timeout=10)
                if response.status_code // 100 == 2:
                    return response
                else:
                    error_message = (response.status_code,
                                     response.text)
                    logger.error(error_message)
            except Exception as e:
                logger.error(e)
            time.sleep(2)

    def get_files_list(self):
        """
        Получает список файлов на облаке в виде списка из словарей
        """
        url = self.main_url + 'resources/'
        params = {
            'path': f'{self.path}',
            'fields': 'name, _embedded.items.path, _embedded.items.name, _embedded.items.modified,'
        }
        response = self.connect(url, params=params, headers=self.headers)
        files = {}
        for file in response.json()["_embedded"]["items"]:
            files[file["name"]] = {'name': file["name"], "path": file["path"], "modified": file["modified"]}
        return files

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
        upload_url = self.connect(url, headers=self.headers, params=params)
        if upload_url:
            url = upload_url.json()["href"]
            with open(create_local_path(filename), 'rb') as file:
                upload_response = self.connect(url, data=file, method="PUT")
                logger.success(f'Файл {filename} успешно выгружен в облако!')

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
        delete_response = self.connect(url, headers=self.headers, params=params, method='DELETE')
        logger.info(f'Файл {filename} успешно удален!')


if __name__ == '__main__':
    Folder = Folder(local_folder_path)
    YFolder = CloudFolder(cloud_folder_path, token)
    Folder.start_logging(YFolder)