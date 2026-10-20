import os
import requests


class CloudStorageError(Exception):
    """Ошибка работы с облачным хранилищем."""


class YandexDisk:
    """Класс для работы с файлами на Яндекс Диске."""

    BASE_URL = "https://cloud-api.yandex.net/v1/disk/resources"

    def __init__(self, token, remote_folder):
        self.token = token
        self.remote_folder = remote_folder
        self.headers = {
            "Authorization": f"OAuth {self.token}"
        }

    def get_remote_path(self, filename):
        return f"disk:/{self.remote_folder}/{filename}"

    def check_connection(self):
        url = "https://cloud-api.yandex.net/v1/disk"
        response = requests.get(url, headers=self.headers, timeout=10)

        if response.status_code == 401:
            raise CloudStorageError(
                "Неверный токен доступа к Яндекс Диску. "
                "Проверьте значение token в config.ini."
            )

        if response.status_code != 200:
            raise CloudStorageError(
                f"Яндекс Диск недоступен. Код ответа: "
                f"{response.status_code}."
            )

    def create_remote_folder(self):
        url = self.BASE_URL
        params = {"path": f"disk:/{self.remote_folder}"}

        response = requests.put(
            url,
            headers=self.headers,
            params=params,
            timeout=10,
        )

        if response.status_code not in (201, 409):
            raise CloudStorageError(
                f"Не удалось создать папку "
                f"'{self.remote_folder}' на Яндекс Диске. "
                f"Код ответа: {response.status_code}."
            )

    def get_upload_url(self, remote_path):
        params = {
            "path": remote_path,
            "overwrite": "true",
        }

        response = requests.get(
            self.BASE_URL + "/upload",
            headers=self.headers,
            params=params,
            timeout=10,
        )

        if response.status_code != 200:
            raise CloudStorageError(
                f"Не удалось получить ссылку для загрузки файла. "
                f"Код ответа: {response.status_code}."
            )

        upload_url = response.json().get("href")

        if not upload_url:
            raise CloudStorageError(
                "Яндекс Диск не вернул ссылку для загрузки файла."
            )

        return upload_url

    def load(self, path):
        filename = os.path.basename(path)
        remote_path = self.get_remote_path(filename)
        upload_url = self.get_upload_url(remote_path)

        with open(path, "rb") as file:
            response = requests.put(upload_url, data=file, timeout=60)

        if response.status_code not in (201, 202):
            raise CloudStorageError(
                f"Не удалось загрузить файл '{filename}' "
                f"на Яндекс Диск. Код ответа: {response.status_code}."
            )

    def reload(self, path):
        self.load(path)

    def delete(self, filename):
        remote_path = self.get_remote_path(filename)
        params = {
            "path": remote_path,
            "permanently": "false",
        }

        response = requests.delete(
            self.BASE_URL,
            headers=self.headers,
            params=params,
            timeout=10,
        )

        if response.status_code not in (204, 202, 404):
            raise CloudStorageError(
                f"Не удалось удалить файл '{filename}' "
                f"с Яндекс Диска. Код ответа: {response.status_code}."
            )

    def get_info(self):
        params = {
            "path": f"disk:/{self.remote_folder}",
            "limit": "1000",
        }

        response = requests.get(
            self.BASE_URL,
            headers=self.headers,
            params=params,
            timeout=10,
        )

        if response.status_code == 404:
            return []

        if response.status_code != 200:
            raise CloudStorageError(
                f"Не удалось получить список файлов "
                f"с Яндекс Диска. Код ответа: {response.status_code}."
            )

        items = response.json().get("_embedded", {}).get("items", [])
        return [item["name"] for item in items if item["type"] == "file"]