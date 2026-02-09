"""
Менеджер тем для PySide6.
Светлая и тёмная темы через QSS стили.
"""

from PySide6.QtWidgets import QApplication


class ThemeColors:
    """Цветовые схемы для тем."""

    LIGHT = {
        'bg': '#f8f9fa',
        'card': '#ffffff',
        'text': '#212529',
        'text_secondary': '#6c757d',
        'accent': '#0d6efd',
        'accent_hover': '#0b5ed7',
        'border': '#dee2e6',
        'input_bg': '#ffffff',
        'success': '#198754',
        'error': '#dc3545',
        'warning': '#ffc107',
    }

    DARK = {
        'bg': '#1a1a2e',
        'card': '#16213e',
        'text': '#e8e8e8',
        'text_secondary': '#a0a0a0',
        'accent': '#4cc9f0',
        'accent_hover': '#3db8df',
        'border': '#2d3748',
        'input_bg': '#1e2a3a',
        'success': '#20c997',
        'error': '#f87171',
        'warning': '#fbbf24',
    }


def get_light_stylesheet() -> str:
    """Получить QSS стили для светлой темы."""
    c = ThemeColors.LIGHT
    return f"""
        /* Основное окно */
        QMainWindow {{
            background-color: {c['bg']};
        }}

        /* Центральный виджет */
        QWidget {{
            background-color: {c['bg']};
            color: {c['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }}

        /* Группы (карточки) */
        QGroupBox {{
            background-color: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding: 15px;
            padding-top: 25px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 8px;
            color: {c['text']};
            background-color: {c['card']};
        }}

        /* Поля ввода */
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 6px 10px;
            color: {c['text']};
            selection-background-color: {c['accent']};
            min-height: 24px;
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c['accent']};
        }}

        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width: 0;
            border: none;
        }}

        /* Кнопки */
        QPushButton {{
            background-color: {c['accent']};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 13px;
        }}

        QPushButton:hover {{
            background-color: {c['accent_hover']};
        }}

        QPushButton:pressed {{
            background-color: #084298;
        }}

        QPushButton:disabled {{
            background-color: {c['border']};
            color: {c['text_secondary']};
        }}

        /* Вторичные кнопки */
        QPushButton[secondary="true"] {{
            background-color: {c['card']};
            color: {c['text']};
            border: 1px solid {c['border']};
        }}

        QPushButton[secondary="true"]:hover {{
            background-color: {c['bg']};
        }}

        /* Кнопка темы */
        QPushButton#themeButton {{
            background-color: transparent;
            border: 1px solid {c['border']};
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 16px;
        }}

        QPushButton#themeButton:hover {{
            background-color: {c['border']};
        }}

        /* Чекбоксы */
        QCheckBox {{
            spacing: 8px;
            color: {c['text']};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border']};
            border-radius: 4px;
            background-color: {c['input_bg']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['accent']};
            border-color: {c['accent']};
        }}

        /* Метки */
        QLabel {{
            color: {c['text']};
            background-color: transparent;
            min-height: 20px;
        }}

        QLabel[secondary="true"] {{
            color: {c['text_secondary']};
            font-size: 11px;
        }}

        /* Кнопка помощи */
        QPushButton[helpButton="true"] {{
            background-color: transparent;
            color: {c['text_secondary']};
            border: 1px solid {c['border']};
            border-radius: 13px;
            font-size: 12px;
            font-weight: bold;
            padding: 0px;
            min-width: 26px;
            max-width: 26px;
            min-height: 26px;
            max-height: 26px;
        }}

        QPushButton[helpButton="true"]:hover {{
            background-color: {c['accent']};
            color: white;
            border-color: {c['accent']};
        }}

        /* Область сообщений */
        QListWidget {{
            background-color: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
            color: {c['text']};
        }}

        QListWidget::item {{
            padding: 4px 8px;
            border-radius: 4px;
        }}

        QListWidget::item:selected {{
            background-color: {c['accent']};
            color: white;
        }}

        /* Полоса прокрутки */
        QScrollBar:vertical {{
            background-color: {c['bg']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['border']};
            border-radius: 6px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['text_secondary']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        /* Заголовок */
        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {c['text']};
        }}

        /* Подсказки */
        QToolTip {{
            background-color: {c['card']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px;
        }}
    """


def get_dark_stylesheet() -> str:
    """Получить QSS стили для тёмной темы."""
    c = ThemeColors.DARK
    return f"""
        /* Основное окно */
        QMainWindow {{
            background-color: {c['bg']};
        }}

        /* Центральный виджет */
        QWidget {{
            background-color: {c['bg']};
            color: {c['text']};
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 14px;
        }}

        /* Группы (карточки) */
        QGroupBox {{
            background-color: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 8px;
            margin-top: 12px;
            padding: 15px;
            padding-top: 25px;
            font-weight: bold;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 12px;
            padding: 0 8px;
            color: {c['text']};
            background-color: {c['card']};
        }}

        /* Поля ввода */
        QLineEdit, QSpinBox, QDoubleSpinBox {{
            background-color: {c['input_bg']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 6px 10px;
            color: {c['text']};
            selection-background-color: {c['accent']};
            min-height: 24px;
        }}

        QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 2px solid {c['accent']};
        }}

        QSpinBox::up-button, QDoubleSpinBox::up-button,
        QSpinBox::down-button, QDoubleSpinBox::down-button {{
            width: 0;
            border: none;
        }}

        /* Кнопки */
        QPushButton {{
            background-color: {c['accent']};
            color: #1a1a2e;
            border: none;
            border-radius: 6px;
            padding: 12px 24px;
            font-weight: bold;
            font-size: 13px;
        }}

        QPushButton:hover {{
            background-color: {c['accent_hover']};
        }}

        QPushButton:pressed {{
            background-color: #2d9ac4;
        }}

        QPushButton:disabled {{
            background-color: {c['border']};
            color: {c['text_secondary']};
        }}

        /* Вторичные кнопки */
        QPushButton[secondary="true"] {{
            background-color: {c['card']};
            color: {c['text']};
            border: 1px solid {c['border']};
        }}

        QPushButton[secondary="true"]:hover {{
            background-color: {c['bg']};
        }}

        /* Кнопка темы */
        QPushButton#themeButton {{
            background-color: transparent;
            border: 1px solid {c['border']};
            border-radius: 20px;
            padding: 8px 16px;
            font-size: 16px;
        }}

        QPushButton#themeButton:hover {{
            background-color: {c['border']};
        }}

        /* Чекбоксы */
        QCheckBox {{
            spacing: 8px;
            color: {c['text']};
        }}

        QCheckBox::indicator {{
            width: 18px;
            height: 18px;
            border: 2px solid {c['border']};
            border-radius: 4px;
            background-color: {c['input_bg']};
        }}

        QCheckBox::indicator:checked {{
            background-color: {c['accent']};
            border-color: {c['accent']};
        }}

        /* Метки */
        QLabel {{
            color: {c['text']};
            background-color: transparent;
            min-height: 20px;
        }}

        QLabel[secondary="true"] {{
            color: {c['text_secondary']};
            font-size: 11px;
        }}

        /* Кнопка помощи */
        QPushButton[helpButton="true"] {{
            background-color: transparent;
            color: {c['text_secondary']};
            border: 1px solid {c['border']};
            border-radius: 13px;
            font-size: 12px;
            font-weight: bold;
            padding: 0px;
            min-width: 26px;
            max-width: 26px;
            min-height: 26px;
            max-height: 26px;
        }}

        QPushButton[helpButton="true"]:hover {{
            background-color: {c['accent']};
            color: #1a1a2e;
            border-color: {c['accent']};
        }}

        /* Область сообщений */
        QListWidget {{
            background-color: {c['card']};
            border: 1px solid {c['border']};
            border-radius: 6px;
            padding: 8px;
            color: {c['text']};
        }}

        QListWidget::item {{
            padding: 4px 8px;
            border-radius: 4px;
        }}

        QListWidget::item:selected {{
            background-color: {c['accent']};
            color: #1a1a2e;
        }}

        /* Полоса прокрутки */
        QScrollBar:vertical {{
            background-color: {c['bg']};
            width: 12px;
            border-radius: 6px;
        }}

        QScrollBar::handle:vertical {{
            background-color: {c['border']};
            border-radius: 6px;
            min-height: 30px;
        }}

        QScrollBar::handle:vertical:hover {{
            background-color: {c['text_secondary']};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}

        /* Заголовок */
        QLabel#titleLabel {{
            font-size: 18px;
            font-weight: bold;
            color: {c['text']};
        }}

        /* Подсказки */
        QToolTip {{
            background-color: {c['card']};
            color: {c['text']};
            border: 1px solid {c['border']};
            border-radius: 4px;
            padding: 8px;
        }}
    """


class ThemeManager:
    """Менеджер переключения тем."""

    LIGHT = "light"
    DARK = "dark"

    @staticmethod
    def apply_theme(app: QApplication, theme: str) -> None:
        """Применить тему к приложению."""
        if theme == ThemeManager.DARK:
            app.setStyleSheet(get_dark_stylesheet())
        else:
            app.setStyleSheet(get_light_stylesheet())

    @staticmethod
    def toggle_theme(current: str) -> str:
        """Переключить тему и вернуть новую."""
        return ThemeManager.DARK if current == ThemeManager.LIGHT else ThemeManager.LIGHT

    @staticmethod
    def get_theme_icon(theme: str) -> str:
        """Получить иконку для текущей темы."""
        return "🌙" if theme == ThemeManager.LIGHT else "☀️"
