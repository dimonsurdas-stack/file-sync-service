import configparser
import os


class ConfigError(Exception):
    """Ошибка параметров запуска программы."""


def read_config(config_path):
    config = configparser.ConfigParser()

    if not os.path.exists(config_path):
        raise ConfigError(
            f"Файл настроек не найден: {config_path}. "
            "Создайте config.ini рядом с main.py."
        )

    config.read(config_path, encoding="utf-8")

    if not config.has_section("settings"):
        raise ConfigError("В config.ini отсутствует секция [settings].")

    settings = {
        "local_folder": config.get("settings", "local_folder", fallback=""),
        "remote_folder": config.get("settings", "remote_folder", fallback=""),
        "token": config.get("settings", "token", fallback=""),
        "sync_period": config.get("settings", "sync_period", fallback=""),
        "log_file": config.get("settings", "log_file", fallback="sync.log"),
    }

    validate_settings(settings)
    return settings


def validate_settings(settings):
    if not settings["local_folder"]:
        raise ConfigError(
            "Не указан путь к синхронизируемой папке "
            "в параметре local_folder."
        )

    if not os.path.isdir(settings["local_folder"]):
        raise ConfigError(
            f"Синхронизируемая папка не существует: "
            f"{settings['local_folder']}. "
            "Проверьте путь в config.ini."
        )

    if not settings["remote_folder"]:
        raise ConfigError(
            "Не указано имя папки в облачном хранилище "
            "в параметре remote_folder."
        )

    if not settings["token"]:
        raise ConfigError(
            "Не указан токен доступа в параметре token. "
            "Получите OAuth-токен Яндекс Диска и добавьте его в config.ini."
        )

    try:
        settings["sync_period"] = int(settings["sync_period"])
    except ValueError:
        raise ConfigError(
            "Параметр sync_period должен быть целым числом "
            "в секундах, например: sync_period = 10."
        )

    if settings["sync_period"] <= 0:
        raise ConfigError(
            "Параметр sync_period должен быть больше нуля."
        )

    if not settings["log_file"]:
        raise ConfigError(
            "Не указан путь к файлу лога в параметре log_file."
        )