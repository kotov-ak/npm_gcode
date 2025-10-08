import os
import sys
import time

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (QMainWindow, QApplication, QFileDialog,
                             QMessageBox, QWidget)

from design.py_files.main import Ui_NPM_Code_Generator
from design.py_files.scheme import Ui_Scheme
from functions.prod_functions import (
    current_time, write_in_file_by_lines, check_params_for_validity
)
from constants.const import *
from functions.tube_g_code_generator import *
from visualization import create_punch_visualization

# Настройки DPI для корректного отображения на мониторах
os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_EnableHighDpiScaling, True)


class CodeGenerationThread(QThread):
    """Поток для генерации G-кода"""
    finished = pyqtSignal(bool, str)

    def __init__(self, advanced_dict, gcode_path):
        super().__init__()
        self.advanced_dict = advanced_dict.copy()
        self.gcode_path = gcode_path

    def run(self):
        try:
            # Генерация G-кода
            g_code_lines = generate_command_lines(self.advanced_dict)

            # Сохранение в файл
            write_in_file_by_lines(g_code_lines, self.gcode_path)

            self.finished.emit(True, self.gcode_path)

        except Exception as e:
            self.finished.emit(False, f"ОШИБКА! Не удалось сгенерировать или сохранить код: {str(e)}")


class SchemeWindow(QWidget, Ui_Scheme):
    """Окно для схемы станка"""

    def __init__(self):
        QWidget.__init__(self)
        self.setupUi(self)


class MainWindow(QMainWindow, Ui_NPM_Code_Generator):
    """Главное окно приложения"""

    def __init__(self):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.scheme = None
        self.params = None
        self.gcode_path = ''
        self.generation_thread = None

        self.code_file_name_search.clicked.connect(self.get_code_filename)

        # меню для помощи
        self.base_info.triggered.connect(self.base_info_display)
        self.scheme_info.triggered.connect(self.show_scheme_window)
        self.version_info.triggered.connect(self.version_info_display)

        # инициализация генерации
        self.generate.clicked.connect(self.gen_code)

        # инициализация визуализации
        self.visualization.clicked.connect(self.gen_visualization)

    def base_info_display(self):
        """Отображение базовой информации из меню"""
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Правила использования программы")
        dlg.setText(base_description)
        dlg.exec()

    def show_scheme_window(self):
        """Отображение схемы из меню"""
        if self.scheme is None:
            self.scheme = SchemeWindow()
        self.scheme.show()

    def version_info_display(self):
        """Отображение версии из меню"""
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Описание текущей версии")
        dlg.setText(version_description)
        dlg.exec()

    def text_to_info_out(self, text):
        """Вывод в 'консоль' приложения текста с меткой времени"""
        self.info_out.insertItem(0, f'{text} в {current_time()}')

    def invalid_chars(self, text):
        """Проверка корректности имени файла"""
        invalid_chars = "'/:*?\"<>+|\\"
        for char in text:
            if char in invalid_chars:
                return True, char
        return False, None

    def get_code_filename(self):
        """Получение файла для кода (путь)"""
        folderpath = QFileDialog.getExistingDirectory(directory='../gcode')
        filename = self.code_filename_input.text()

        if not folderpath:
            self.text_to_info_out('ОШИБКА! Папка для сохранения не выбрана')
            return

        if not filename:
            self.text_to_info_out('ОШИБКА! Имя файла для сохранения не задано')
            return

        has_invalid_char, invalid_char = self.invalid_chars(filename)
        if has_invalid_char:
            self.text_to_info_out(f'ОШИБКА! Имя файла содержит недопустимый символ "{invalid_char}"')
            return

        self.gcode_path = os.path.join(folderpath, f"{filename}.txt")
        self.text_to_info_out(f'{self.gcode_path}')
        self.info_out.insertItem(0, 'Код будет сохранен в:')

    def input_values_update(self):
        """Считывание данных введенных вручную"""
        values_list = [self.tube_len,
                       self.i_dia,
                       self.o_dia,
                       self.fab_thick,
                       self.punch_step_r,
                       self.needle_step,
                       self.volumetric_density,
                       self.punch_head_len,
                       self.punch_depth,
                       self.needle_offset,
                       self.shoe_depth,
                       self.idling_speed,
                       self.move_speed,
                       self.rotate_speed,
                       self.random_border]

        try:
            for key, widget in zip(advanced_dict.keys(), values_list):
                advanced_dict[key] = widget.value()
            return True
        except Exception as e:
            print(f"Ошибка при обновлении значений: {e}")
            return False

    def on_generation_finished(self, success, message):
        """Обработчик завершения генерации"""
        if success:
            self.text_to_info_out(message)
            self.info_out.insertItem(0, 'Код успешно сгенерирован и находится в: ')
            self.info_out.insertItem(0,
                                     'Выполнена генерация стандартного режима пробития на основе данных, введенных вручную')
        else:
            self.text_to_info_out(message)

        # Разблокируем кнопку
        self.generate.setEnabled(True)
        self.generation_thread = None

    def gen_code(self):
        """Генерация кода. Определение кода генерации"""

        # Блокируем кнопку на время выполнения
        self.generate.setEnabled(False)

        # Проверяем, что путь сохранения установлен
        if not self.gcode_path:
            self.text_to_info_out('ОШИБКА! Код НЕ сгенерирован, ошибка в пути сохранения файла')
            self.generate.setEnabled(True)
            return

        # Получаем текущие выбранные режимы
        current_punch_mode = self.punch_mode.currentText()
        current_data_mode = self.data_mode.currentText()

        # Создаем идентификатор режима
        mode_id = (current_punch_mode, current_data_mode)

        # Ищем обработчик для этого режима
        handler_name = MODE_HANDLERS.get(mode_id)

        if not handler_name:
            self.text_to_info_out(
                f'ОШИБКА! Комбинация режимов не поддерживается: {current_punch_mode} + {current_data_mode}')
            self.generate.setEnabled(True)
            return

        # Обновляем значения параметров
        if not self.input_values_update():
            self.text_to_info_out('ОШИБКА! Не удалось обновить значения параметров')
            self.generate.setEnabled(True)
            return

        # Проверяем параметры на валидность
        is_valid, invalid_param, error_message = check_params_for_validity(advanced_dict)

        if not is_valid:
            error_msg = f'Ошибка в параметре "{invalid_param}": {error_message}'
            self.text_to_info_out(error_msg)
            self.text_to_info_out('ОШИБКА! Код НЕ сгенерирован, ошибка в значениях параметров')
            self.generate.setEnabled(True)
            return

        # Запускаем генерацию в отдельном потоке
        if handler_name == "punch_mode_11":
            # Показываем сообщение о начале генерации
            self.text_to_info_out("Начало генерации кода...")

            # Создаем и запускаем поток
            self.generation_thread = CodeGenerationThread(advanced_dict, self.gcode_path)
            self.generation_thread.finished.connect(self.on_generation_finished)
            self.generation_thread.start()

    def closeEvent(self, event):
        """Обработчик закрытия окна - останавливаем поток если он запущен"""
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.generation_thread.wait()
        event.accept()

    def gen_visualization(self):
        """Генерация визуализации паттерна пробития"""
        print("[GUI] === НАЧАЛО ГЕНЕРАЦИИ ВИЗУАЛИЗАЦИИ ===")

        # Обновляем значения параметров
        print("[GUI] Обновление значений параметров...")
        if not self.input_values_update():
            self.text_to_info_out('ОШИБКА! Не удалось обновить значения параметров')
            print("[GUI] ОШИБКА: Не удалось обновить значения параметров")
            return

        print("[GUI] Параметры успешно обновлены")

        # Проверяем параметры на валидность
        print("[GUI] Проверка валидности параметров...")
        is_valid, invalid_param, error_message = check_params_for_validity(advanced_dict)

        if not is_valid:
            error_msg = f'Ошибка в параметре "{invalid_param}": {error_message}'
            self.text_to_info_out(error_msg)
            self.text_to_info_out('ОШИБКА! Визуализация НЕ создана, ошибка в значениях параметров')
            print(f"[GUI] ОШИБКА валидации: {error_msg}")
            return

        print("[GUI] Параметры прошли валидацию")

        try:
            # Создаем путь для HTML файла
            html_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "viz/visualization.html")

            print(f"[GUI] Запуск визуализации с путем: {html_path}")
            print("[GUI] Параметры визуализации:")
            for key, value in advanced_dict.items():
                print(f"[GUI]   {key}: {value}")

            # Генерируем визуализацию
            create_punch_visualization(advanced_dict, html_path)

            self.text_to_info_out(f"Визуализация сохранена в: {html_path}")
            self.text_to_info_out("Визуализация успешно создана")
            print("[GUI] Визуализация успешно завершена")

        except Exception as e:
            error_msg = f"ОШИБКА! Не удалось создать визуализацию: {str(e)}"
            self.text_to_info_out(error_msg)

            # Подробный вывод в консоль
            print(f"[GUI] КРИТИЧЕСКАЯ ОШИБКА визуализации: {e}")
            print(f"[GUI] Тип ошибки: {type(e).__name__}")
            print(f"[GUI] Путь HTML файла: {html_path if 'html_path' in locals() else 'Не определен'}")
            print("[GUI] Полный стек ошибки:")
            import traceback
            traceback.print_exc()


def app_show():
    """Запуск основного приложения"""
    app = (QtWidgets.QApplication.instance() or
           QtWidgets.QApplication(sys.argv))
    main = MainWindow()
    main.show()
    sys.exit(app.exec_())


