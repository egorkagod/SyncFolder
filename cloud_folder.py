import requests
import time
from typing import Dict, Optional, Union
from requests import Response

from settings import logger


class CloudFolder:
    """Описывает папку на облачном сервисе"""

    main_url = 'https://cloud-api.yandex.net/v1/disk/'

    def __init__(self, path: str, token: str) -> None:
        """
        Инициализация объекта CloudFolder.

        :param path: Путь к папке в облаке.
        :param token: OAuth токен для авторизации.
        """
        self.path = path
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': f'OAuth {token}'
        }
        self.local: Union[bool, 'Folder'] = False

    def is_connected(self) -> None:
        """
        Проверяет, есть ли локальный аналог у облачной папки.

        :raises Exception: Если локального аналога нет.
        """
        if not self.local:
            raise Exception('У облачной папки нет локального аналога!')

    def create_remote_path(self, filename: str) -> str:
        """
        Создает удаленный путь для файла.

        :param filename: Имя файла.
        :return: Полный путь к файлу в облаке.
        """
        return f'{self.path}/{filename}'

    def connect(self, url: str, headers: Optional[Dict[str, str]] = None,
                params: Optional[Dict[str, str]] = None,
                data: Optional[Union[bytes, str]] = None, method: str = 'GET') -> Optional[Response]:
        """
        Устанавливает соединение с облачным сервисом.

        :param url: URL для запроса.
        :param headers: Заголовки для запроса.
        :param params: Параметры для запроса.
        :param data: Данные для запроса.
        :param method: Метод запроса (GET, POST, PUT, DELETE).
        :return: Ответ сервера.
        """
        while True:
            try:
                response = requests.request(method, url, headers=headers, params=params, data=data, timeout=10)
                if response.status_code // 100 == 2:
                    return response
                else:
                    logger.error((response.status_code, response.text))
            except Exception as e:
                logger.error(e)
            time.sleep(2)

    def get_files_list(self) -> Dict[str, Dict[str, str]]:
        """
        Получает список файлов на облаке в виде словаря.

        :return: Словарь с информацией о файлах.
        """
        url = self.main_url + 'resources/'
        params = {
            'path': self.path,
            'fields': 'name, _embedded.items.path, _embedded.items.name, _embedded.items.modified'
        }
        response = self.connect(url, params=params, headers=self.headers)
        files = {}
        if response:
            for file in response.json()["_embedded"]["items"]:
                files[file["name"]] = {
                    'name': file["name"],
                    "path": file["path"],
                    "modified": file["modified"]
                }
        return files

    def upload_file(self, filename: str) -> None:
        """
        Загружает файл на облако.

        :param filename: Имя файла для загрузки.
        """
        self.is_connected()
        url = self.main_url + 'resources/upload/'
        params = {
            'path': self.create_remote_path(filename),
            'overwrite': 'true',
        }
        upload_url = self.connect(url, headers=self.headers, params=params)
        if upload_url:
            url = upload_url.json()["href"]
            with open(self.local.create_local_path(filename), 'rb') as file:
                self.connect(url, data=file, method="PUT")
                logger.success(f'Файл {filename} успешно выгружен в облако!')

    def delete_file(self, filename: str) -> None:
        """
        Удаляет файл с облака.

        :param filename: Имя файла для удаления.
        """
        url = self.main_url + 'resources/'
        params = {
            'path': self.create_remote_path(filename),
            'permanently': 'true',
        }
        self.connect(url, headers=self.headers, params=params, method='DELETE')
        logger.info(f'Файл {filename} успешно удален!')
