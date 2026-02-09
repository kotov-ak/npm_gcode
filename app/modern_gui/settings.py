"""
Менеджер настроек для сохранения параметров между сессиями.
Использует JSON файл для хранения.
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from constants.const import advanced_dict


class SettingsManager:
    """Управление настройками приложения с сохранением в JSON."""

    VERSION = "1.0"

    def __init__(self):
        self.settings_path = self._get_settings_path()
        self.settings = self._load_settings()

    def _get_settings_path(self) -> Path:
        """Получить путь к файлу настроек в зависимости от ОС."""
        if os.name == 'nt':  # Windows
            base = Path(os.environ.get('APPDATA', Path.home()))
            config_dir = base / 'NPM_GCode_Generator'
        else:  # Linux/Mac
            base = Path.home() / '.config'
            config_dir = base / 'npm_gcode_generator'

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / 'settings.json'

    def _get_default_settings(self) -> Dict[str, Any]:
        """Получить настройки по умолчанию."""
        return {
            "version": self.VERSION,
            "theme": "light",
            "parameters": dict(advanced_dict),
            "file_preferences": {
                "save_to_desktop": False,
                "last_filename": "gcode_output"
            }
        }

    def _load_settings(self) -> Dict[str, Any]:
        """Загрузить настройки из файла или создать по умолчанию."""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Слияние с дефолтными для добавления новых ключей
                    defaults = self._get_default_settings()
                    defaults.update(loaded)
                    # Обновляем параметры - добавляем новые из advanced_dict
                    for key, value in advanced_dict.items():
                        if key not in defaults["parameters"]:
                            defaults["parameters"][key] = value
                    return defaults
            except (json.JSONDecodeError, KeyError):
                return self._get_default_settings()
        return self._get_default_settings()

    def _save_settings(self) -> None:
        """Сохранить настройки в файл."""
        try:
            with open(self.settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения настроек: {e}")

    # Работа с темой
    def get_theme(self) -> str:
        """Получить текущую тему."""
        return self.settings.get("theme", "light")

    def set_theme(self, theme: str) -> None:
        """Установить тему и сохранить."""
        self.settings["theme"] = theme
        self._save_settings()

    # Работа с параметрами
    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Получить значение параметра."""
        return self.settings["parameters"].get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        """Установить значение параметра."""
        self.settings["parameters"][key] = value
        self._save_settings()

    def get_all_parameters(self) -> Dict[str, Any]:
        """Получить все параметры."""
        return self.settings["parameters"].copy()

    def set_all_parameters(self, params: Dict[str, Any]) -> None:
        """Установить все параметры и сохранить."""
        self.settings["parameters"].update(params)
        self._save_settings()

    # Работа с файловыми настройками
    def get_save_to_desktop(self) -> bool:
        """Получить флаг сохранения на рабочий стол."""
        return self.settings["file_preferences"].get("save_to_desktop", False)

    def set_save_to_desktop(self, value: bool) -> None:
        """Установить флаг сохранения на рабочий стол."""
        self.settings["file_preferences"]["save_to_desktop"] = value
        self._save_settings()

    def get_last_filename(self) -> str:
        """Получить последнее имя файла."""
        return self.settings["file_preferences"].get("last_filename", "gcode_output")

    def set_last_filename(self, filename: str) -> None:
        """Установить последнее имя файла."""
        self.settings["file_preferences"]["last_filename"] = filename
        self._save_settings()
