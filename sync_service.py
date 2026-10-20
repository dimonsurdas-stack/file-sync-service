import logging
import os
import time


class FileSyncService:
    """Сервис синхронизации локальной папки с Яндекс Диском."""

    def __init__(self, local_folder, cloud_storage, logger):
        self.local_folder = local_folder
        self.cloud_storage = cloud_storage
        self.logger = logger
        self.local_files = {}

    def start(self, sync_period):
        self.logger.info(
            "Программа запущена. Синхронизируемая папка: %s",
            self.local_folder,
        )
        self.initial_sync()

        while True:
            self.sync()
            time.sleep(sync_period)

    def initial_sync(self):
        self.cloud_storage.check_connection()
        self.cloud_storage.create_remote_folder()

        remote_files = self.cloud_storage.get_info()
        local_files = self.get_local_files()

        self.delete_extra_remote_files(remote_files, local_files)

        for filename in local_files:
            self.upload_file(filename)

        self.local_files = local_files

    def sync(self):
        try:
            current_files = self.get_local_files()
            self.process_deleted_files(current_files)
            self.process_new_files(current_files)
            self.process_changed_files(current_files)
            self.local_files = current_files
        except Exception as error:
            self.logger.error("Ошибка синхронизации: %s", error)

    def get_local_files(self):
        files = {}

        for filename in os.listdir(self.local_folder):
            file_path = os.path.join(self.local_folder, filename)

            if os.path.isfile(file_path):
                files[filename] = os.path.getmtime(file_path)

        return files

    def process_new_files(self, current_files):
        for filename in current_files:
            if filename not in self.local_files:
                self.upload_file(filename)

    def process_changed_files(self, current_files):
        for filename, modification_time in current_files.items():
            old_time = self.local_files.get(filename)

            if old_time is not None and modification_time != old_time:
                self.reload_file(filename)

    def process_deleted_files(self, current_files):
        deleted_files = set(self.local_files) - set(current_files)

        for filename in deleted_files:
            self.delete_file(filename)

    def delete_extra_remote_files(self, remote_files, local_files):
        extra_files = set(remote_files) - set(local_files)

        for filename in extra_files:
            self.delete_file(filename)

    def upload_file(self, filename):
        file_path = os.path.join(self.local_folder, filename)

        try:
            self.cloud_storage.load(file_path)
            self.logger.info("Файл загружен: %s", filename)
        except Exception as error:
            self.logger.error(
                "Не удалось загрузить файл '%s': %s",
                filename,
                error,
            )

    def reload_file(self, filename):
        file_path = os.path.join(self.local_folder, filename)

        try:
            self.cloud_storage.reload(file_path)
            self.logger.info("Файл обновлён: %s", filename)
        except Exception as error:
            self.logger.error(
                "Не удалось обновить файл '%s': %s",
                filename,
                error,
            )

    def delete_file(self, filename):
        try:
            self.cloud_storage.delete(filename)
            self.logger.info("Файл удалён: %s", filename)
        except Exception as error:
            self.logger.error(
                "Не удалось удалить файл '%s': %s",
                filename,
                error,
            )