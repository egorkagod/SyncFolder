from settings import LOCAL_FOLDER_PATH, CLOUD_FOLDER_PATH, PERIOD, TOKEN
from folder import Folder
from cloud_folder import CloudFolder

if __name__ == '__main__':
    local_folder = Folder(LOCAL_FOLDER_PATH)
    cloud_folder = CloudFolder(CLOUD_FOLDER_PATH, TOKEN)
    local_folder.do_connection(cloud_folder)
    local_folder.start_logging(PERIOD)
