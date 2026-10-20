import logging

from config_reader import ConfigError, read_config
from sync_service import FileSyncService
from yandex_disk import CloudStorageError, YandexDisk

def setup_logger(log_file):
    logger = logging.getLogger("file_sync")
    logger.setLevel(logging.INFO)

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger


def run_application():
    try:
        settings = read_config("config.ini")
    except ConfigError as error:
        print(f"Ошибка настроек: {error}")
        return

    logger = setup_logger(settings["log_file"])
    cloud_storage = YandexDisk(
        settings["token"],
        settings["remote_folder"],
    )

    try:
        cloud_storage.check_connection()
    except CloudStorageError as error:
        print(f"Ошибка подключения к Яндекс Диску: {error}")
        logger.error("Ошибка подключения к Яндекс Диску: %s", error)
        return

    sync_service = FileSyncService(
        settings["local_folder"],
        cloud_storage,
        logger,
    )

    try:
        sync_service.start(settings["sync_period"])
    except KeyboardInterrupt:
        print("Программа остановлена пользователем.")
        logger.info("Программа остановлена пользователем.")
    except Exception as error:
        print(f"Непредвиденная ошибка: {error}")
        logger.error("Непредвиденная ошибка: %s", error)


if __name__ == "__main__":
    run_application()