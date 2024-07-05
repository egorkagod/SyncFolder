import os
from datetime import datetime
import time
from typing import Dict, Any

from settings import logger
from cloud_folder import CloudFolder


class Folder:
    """
    Описывает папку операционной системы.
    """

    def __init__(self, path: str) -> None:
        self.is_connect: bool = False
        if os.path.isdir(path):
            self.path: str = path
        else:
            raise Exception('Переданный путь из .env приводит не к папке!')

    def create_local_path(self, filename: str) -> str:
        """
        Создает полный путь для файла в локальной папке.

        :param filename: Имя файла
        :return: Полный путь к файлу
        """
        return os.path.join(self.path, filename)

    def do_connection(self, cloud_folder: CloudFolder) -> None:
        """
        Устанавливает соединение с облачной папкой.

        :param cloud_folder: Объект класса CloudFolder
        """
        if isinstance(cloud_folder, CloudFolder):
            self.is_connect = True
            self.remote = cloud_folder
            cloud_folder.local = self

    def is_connected(self) -> None:
        """
        Проверяет, подключена ли облачная папка.
        """
        if not self.is_connect:
            raise Exception('Не подключена облачная папка!')

    def get_files_list(self) -> Dict[str, Dict[str, Any]]:
        """
        Получает список файлов в локальной папке.

        :return: Словарь с информацией о файлах
        """
        files = {}
        for filename in os.listdir(self.path):
            path = self.create_local_path(filename)
            files[filename] = {
                'name': filename,
                'path': path,
                'modified': datetime.utcfromtimestamp(os.path.getmtime(path)).isoformat()
            }
        return files

    def download_file(self, filename: str) -> None:
        """
        Загружает файл из облачной папки.

        :param filename: Имя файла
        """
        url = self.remote.main_url + 'resources/download/'
        params = {
            'path': self.remote.create_remote_path(filename),
        }
        download_url = self.remote.connect(url, headers=self.remote.headers, params=params)
        if download_url:
            url = download_url.json()["href"]
            with open(self.create_local_path(filename), 'wb') as file:
                download_response = self.remote.connect(url)
                file.write(download_response.content)
                logger.success(f'Файл {filename} успешно скачан с облака!')

    def first_sync_modifications(self) -> None:
        """
        Синхронизирует файлы по времени последнего изменения.
        """
        local_files = self.get_files_list()
        cloud_files = self.remote.get_files_list()
        intersection = set(local_files) & set(cloud_files)
        for filename in intersection:
            if cloud_files[filename]['modified'] > local_files[filename]['modified']:
                self.download_file(filename)
            elif cloud_files[filename]['modified'] < local_files[filename]['modified']:
                self.remote.upload_file(filename)

    def first_sync_by_name(self) -> None:
        """
        Синхронизирует файлы по наличию имени файла.
        """
        file_set = set(self.get_files_list())
        cloud_set = set(self.remote.get_files_list())
        add_to_local = cloud_set - file_set
        add_to_cloud = file_set - cloud_set
        for filename in add_to_local:
            self.download_file(filename)
        for filename in add_to_cloud:
            self.remote.upload_file(filename)

    def first_sync(self) -> None:
        """
        Выполняет первую синхронизацию файлов.
        """
        self.first_sync_modifications()
        self.first_sync_by_name()
        logger.success('Первичная синхронизация прошла успешно!')

    def start_logging(self, period: int = 5) -> None:
        """
        Начинает логирование изменений в файлах.

        :param period: Период логирования в секундах
        """
        self.is_connected()
        self.first_sync()
        while True:
            files_before = self.get_files_list()
            time.sleep(period)
            self.logging_files(files_before)

    def logging_files_by_names(self, files_before: set) -> None:
        """
        Логирует изменения в файлах по именам.

        :param files_before: Список файлов до изменений
        """
        files_now = set(self.get_files_list())
        add_set = files_now - files_before
        remove_set = files_before - files_now
        for filename in add_set:
            self.remote.upload_file(filename)
        for filename in remove_set:
            self.remote.delete_file(filename)

    def logging_files(self, files_before: Dict[str, Dict[str, Any]]) -> None:
        """
        Логирует изменения в файлах.

        :param files_before: Список файлов до изменений
        """
        files_now = self.get_files_list()
        intersection = set(files_before) & set(files_now)
        for filename in intersection:
            if files_now[filename]['modified'] > files_before[filename]['modified']:
                self.remote.upload_file(filename)
        self.logging_files_by_names(set(files_before))
