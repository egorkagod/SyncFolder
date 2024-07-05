# Проект синхронизации папок

## Описание проекта
Этот проект предоставляет функциональность для синхронизации локальной папки с облачной папкой на Yandex Disk. Он включает в себя классы и методы для работы с файлами и папками, а также для синхронизации содержимого между локальной и облачной папками.

## Установка
1. Клонируйте репозиторий:
    ```sh
    git https://github.com/egorkagod/SyncFolder.git
    ```
2. Установите необходимые зависимости:
    ```sh
    pip install -r requirements.txt
    ```

## Использование
### Пример использования
```python
from cloud_folder import CloudFolder
from folder import Folder

local_folder = Folder('/path/to/local/folder')
cloud_folder = CloudFolder('/path/to/cloud/folder')

local_folder.do_connection(cloud_folder)
local_folder.start_logging(period=10)
