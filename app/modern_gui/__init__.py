"""
Современный GUI модуль для генератора G-кода.
Использует PySide6 с поддержкой светлой/тёмной темы.
"""

import sys
import os

from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt

from .main_window import ModernMainWindow
from .themes import ThemeManager
from .settings import SettingsManager


def app_show():
    """Запуск современного GUI приложения."""
    # Включаем поддержку High DPI
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    # Создаём или получаем экземпляр приложения
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Включаем High DPI атрибуты
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # Загружаем сохранённую тему
    settings = SettingsManager()
    ThemeManager.apply_theme(app, settings.get_theme())

    # Создаём и показываем главное окно
    window = ModernMainWindow()
    window.show()

    # Запускаем цикл событий
    sys.exit(app.exec())


__all__ = ['app_show', 'ModernMainWindow', 'ThemeManager', 'SettingsManager']
