#!/usr/bin/env python3
"""
Тесты GUI приложения
"""

import sys
import os
import unittest

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from app import gui_app


class TestGUI(unittest.TestCase):
    """Тесты GUI приложения"""

    def test_gui_application_launch(self):
        """
        Smoke test: проверка запуска GUI приложения
        """
        # Создаем экземпляр приложения
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Создаем главное окно
        window = gui_app.MainWindow()

        # Закрываем окно через короткий таймер (100 мс)
        QTimer.singleShot(100, window.close)
        QTimer.singleShot(150, app.quit)

        # Показываем окно
        window.show()

        # Запускаем event loop на короткое время
        app.exec_()

        print("\n✅ GUI приложение успешно запустилось и закрылось без исключений")


if __name__ == '__main__':
    unittest.main(verbosity=2)
