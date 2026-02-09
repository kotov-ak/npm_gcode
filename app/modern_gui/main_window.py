"""
Главное окно современного интерфейса.
PySide6 реализация с поддержкой тем и сохранением настроек.
"""

import os

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QGroupBox, QLabel, QPushButton, QLineEdit, QCheckBox,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QIcon

from .settings import SettingsManager
from .themes import ThemeManager
from .widgets import ParameterWidget
from .file_utils import get_save_path, validate_filename

from constants.const import advanced_dict
from functions.prod_functions import (
    generate_command_lines, write_in_file_by_lines, check_params_for_validity
)
from visualization import create_punch_visualization


class CodeGenerationThread(QThread):
    """Поток для генерации G-кода."""
    finished = Signal(str)  # gcode_path

    def __init__(self, params: dict, gcode_path: str):
        super().__init__()
        self.params = params.copy()
        self.gcode_path = gcode_path

    def run(self):
        g_code_lines = generate_command_lines(self.params)
        write_in_file_by_lines(g_code_lines, self.gcode_path)
        self.finished.emit(self.gcode_path)


class ModernMainWindow(QMainWindow):
    """Современное главное окно приложения."""

    def __init__(self):
        super().__init__()

        self.settings = SettingsManager()
        self.current_theme = self.settings.get_theme()
        self.generation_thread = None
        self.param_widgets: dict[str, ParameterWidget] = {}

        self._setup_window()
        self._setup_ui()
        self._load_settings()
        self._apply_theme()

    def _setup_window(self):
        """Настройка основных свойств окна."""
        self.setWindowTitle('Генератор G-кода для ИПС "Муравьед"')
        self.setMinimumSize(950, 550)
        self.resize(1000, 600)

        # Иконка приложения
        icon_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'design', 'pictures', 'needle_icon.png'
        )
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _setup_ui(self):
        """Создание интерфейса."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Заголовок с кнопкой темы
        header = self._create_header()
        main_layout.addLayout(header)

        # Основная область с параметрами
        params_layout = QHBoxLayout()
        params_layout.setSpacing(15)

        # Левая колонка
        left_column = QVBoxLayout()
        left_column.setSpacing(15)
        left_column.addWidget(self._create_workpiece_group())
        left_column.addWidget(self._create_needle_group())
        left_column.addStretch()
        params_layout.addLayout(left_column, 1)

        # Центральная колонка
        center_column = QVBoxLayout()
        center_column.setSpacing(15)
        center_column.addWidget(self._create_punch_group())
        center_column.addWidget(self._create_speed_group())
        center_column.addStretch()
        params_layout.addLayout(center_column, 1)

        # Правая колонка
        right_column = QVBoxLayout()
        right_column.setSpacing(15)
        right_column.addWidget(self._create_offset_group())
        right_column.addWidget(self._create_file_group())
        right_column.addStretch()
        params_layout.addLayout(right_column, 1)

        main_layout.addLayout(params_layout)

        # Кнопки действий
        buttons_layout = self._create_buttons()
        main_layout.addLayout(buttons_layout)

    def _create_header(self) -> QHBoxLayout:
        """Создание заголовка с кнопкой темы."""
        layout = QHBoxLayout()

        # Заголовок
        title = QLabel('Генератор G-кода для ИПС "Муравьед"')
        title.setObjectName("titleLabel")
        layout.addWidget(title)

        layout.addStretch()

        # Кнопка темы
        self.theme_button = QPushButton(ThemeManager.get_theme_icon(self.current_theme))
        self.theme_button.setObjectName("themeButton")
        self.theme_button.clicked.connect(self._toggle_theme)
        self.theme_button.setFixedSize(50, 40)
        layout.addWidget(self.theme_button)

        return layout

    def _create_param_widget(self, param_name: str) -> ParameterWidget:
        """Создать виджет параметра и сохранить ссылку."""
        value = self.settings.get_parameter(param_name, advanced_dict.get(param_name, 0))
        widget = ParameterWidget(param_name, value)
        widget.valueChanged.connect(self._on_param_changed)
        self.param_widgets[param_name] = widget
        return widget

    def _create_workpiece_group(self) -> QGroupBox:
        """Группа параметров заготовки."""
        group = QGroupBox("Заготовка")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        for param in ['tube_len', 'i_diam', 'o_diam', 'fabric_thickness']:
            layout.addWidget(self._create_param_widget(param))

        layout.addStretch()
        return group

    def _create_punch_group(self) -> QGroupBox:
        """Группа параметров пробития."""
        group = QGroupBox("Пробитие")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        for param in ['punch_step_r', 'volumetric_density', 'punch_depth']:
            layout.addWidget(self._create_param_widget(param))

        layout.addStretch()
        return group

    def _create_needle_group(self) -> QGroupBox:
        """Группа параметров игольницы."""
        group = QGroupBox("Игольница")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        for param in ['needle_step_X', 'needle_step_Y', 'head_len',
                      'support_depth', 'num_of_needle_rows']:
            layout.addWidget(self._create_param_widget(param))

        layout.addStretch()
        return group

    def _create_speed_group(self) -> QGroupBox:
        """Группа параметров скорости."""
        group = QGroupBox("Скорость")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        for param in ['idling_speed', 'move_speed', 'rotate_speed']:
            layout.addWidget(self._create_param_widget(param))

        layout.addStretch()
        return group

    def _create_offset_group(self) -> QGroupBox:
        """Группа параметров смещений."""
        group = QGroupBox("Смещения")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(8)

        for param in ['punch_offset', 'zero_offset_Y', 'zero_offset_Z', 'random_border']:
            layout.addWidget(self._create_param_widget(param))

        layout.addStretch()
        return group

    def _create_file_group(self) -> QGroupBox:
        """Группа настроек сохранения файла."""
        group = QGroupBox("Сохранение файла")
        group.setMinimumWidth(300)
        layout = QVBoxLayout(group)
        layout.setSpacing(12)

        # Имя файла
        filename_label = QLabel("Имя файла:")
        layout.addWidget(filename_label)

        self.filename_input = QLineEdit()
        self.filename_input.setPlaceholderText("gcode_output")
        self.filename_input.setText(self.settings.get_last_filename())
        self.filename_input.textChanged.connect(self._on_filename_changed)
        layout.addWidget(self.filename_input)

        # Чекбокс "На рабочий стол"
        self.desktop_checkbox = QCheckBox("Сохранить на рабочий стол")
        self.desktop_checkbox.setChecked(self.settings.get_save_to_desktop())
        self.desktop_checkbox.toggled.connect(self._on_desktop_toggled)
        layout.addWidget(self.desktop_checkbox)

        layout.addStretch()
        return group

    def _create_buttons(self) -> QHBoxLayout:
        """Создание кнопок действий."""
        layout = QHBoxLayout()
        layout.setSpacing(15)

        # Визуализация
        self.viz_button = QPushButton("Визуализация")
        self.viz_button.setProperty("secondary", True)
        self.viz_button.clicked.connect(self._generate_visualization)
        self.viz_button.setMinimumHeight(50)
        layout.addWidget(self.viz_button)

        # Генерация
        self.generate_button = QPushButton("Сгенерировать G-код")
        self.generate_button.clicked.connect(self._generate_code)
        self.generate_button.setMinimumHeight(50)
        layout.addWidget(self.generate_button)

        return layout

    def _apply_theme(self):
        """Применить текущую тему."""
        app = QApplication.instance()
        if app:
            ThemeManager.apply_theme(app, self.current_theme)
            self.theme_button.setText(ThemeManager.get_theme_icon(self.current_theme))

    def _toggle_theme(self):
        """Переключить тему."""
        self.current_theme = ThemeManager.toggle_theme(self.current_theme)
        self.settings.set_theme(self.current_theme)
        self._apply_theme()

    def _load_settings(self):
        """Загрузить настройки в виджеты."""
        saved_params = self.settings.get_all_parameters()
        for name, widget in self.param_widgets.items():
            if name in saved_params:
                widget.setValue(saved_params[name])

    def _on_param_changed(self, param_name: str, value: float):
        """Обработчик изменения параметра."""
        self.settings.set_parameter(param_name, value)

    def _on_filename_changed(self, text: str):
        """Обработчик изменения имени файла."""
        self.settings.set_last_filename(text)

    def _on_desktop_toggled(self, checked: bool):
        """Обработчик изменения чекбокса рабочего стола."""
        self.settings.set_save_to_desktop(checked)

    def _get_current_params(self) -> dict:
        """Получить текущие значения параметров."""
        params = {}
        for name, widget in self.param_widgets.items():
            params[name] = widget.value()
        return params

    def _update_advanced_dict(self):
        """Обновить advanced_dict текущими значениями."""
        for name, widget in self.param_widgets.items():
            if name in advanced_dict:
                advanced_dict[name] = widget.value()

    def _validate_params(self) -> tuple[bool, str]:
        """Проверить параметры на валидность."""
        self._update_advanced_dict()
        is_valid, invalid_param, error_message = check_params_for_validity(advanced_dict)
        if not is_valid:
            return False, f'Ошибка в параметре "{invalid_param}": {error_message}'
        return True, ""

    def _get_filename(self) -> str:
        """Получить имя файла."""
        filename = self.filename_input.text().strip()
        if not filename:
            filename = "gcode_output"
        return filename

    def _generate_code(self):
        """Генерация G-кода."""
        # Проверка имени файла
        filename = self._get_filename()
        is_valid, invalid_char = validate_filename(filename)
        if not is_valid:
            QMessageBox.warning(
                self, "Ошибка",
                f'Недопустимый символ "{invalid_char}" в имени файла'
            )
            return

        # Проверка параметров
        valid, error = self._validate_params()
        if not valid:
            QMessageBox.warning(self, "Ошибка", error)
            return

        # Получаем путь сохранения
        save_to_desktop = self.desktop_checkbox.isChecked()
        gcode_path = str(get_save_path(filename, save_to_desktop))

        # Блокируем кнопку
        self.generate_button.setEnabled(False)

        # Запускаем генерацию в потоке (используем полный advanced_dict)
        self.generation_thread = CodeGenerationThread(advanced_dict.copy(), gcode_path)
        self.generation_thread.finished.connect(self._on_generation_finished)
        self.generation_thread.start()

    def _on_generation_finished(self, gcode_path: str):
        """Обработчик завершения генерации."""
        self.generate_button.setEnabled(True)
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Успех")
        msg.setText("G-код успешно сгенерирован и сохранён:")
        msg.setInformativeText(gcode_path)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        self.generation_thread = None

    def _generate_visualization(self):
        """Генерация визуализации."""
        # Проверка параметров
        valid, error = self._validate_params()
        if not valid:
            QMessageBox.warning(self, "Ошибка", error)
            return

        # Путь для HTML
        html_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "visualization.html"
        )

        # Генерация
        create_punch_visualization(advanced_dict, html_path)

        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Успех")
        msg.setText("Визуализация создана:")
        msg.setInformativeText(html_path)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()

    def closeEvent(self, event):
        """Обработчик закрытия окна."""
        if self.generation_thread and self.generation_thread.isRunning():
            self.generation_thread.terminate()
            self.generation_thread.wait()
        event.accept()
