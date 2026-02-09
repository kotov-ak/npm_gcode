"""
Виджеты для параметров с подсказками.
Включает ParameterWidget с кнопкой [?] и всплывающей подсказкой.
"""

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QDoubleSpinBox, QPushButton, QSizePolicy
)
from PySide6.QtCore import Qt, Signal

from .tooltips import TOOLTIPS, PARAMETER_LABELS, PARAMETER_CONFIG


class ParameterWidget(QWidget):
    """
    Виджет для одного параметра.
    Содержит: лейбл, поле ввода, кнопку помощи.
    """

    valueChanged = Signal(str, float)  # (param_name, new_value)

    def __init__(
        self,
        param_name: str,
        initial_value: float = 0.0,
        parent: QWidget = None
    ):
        super().__init__(parent)

        self.param_name = param_name
        self.label_text = PARAMETER_LABELS.get(param_name, param_name)
        self.tooltip_text = TOOLTIPS.get(param_name, "")
        self.config = PARAMETER_CONFIG.get(param_name, (0, 100, 1, 1))

        self._setup_ui(initial_value)

    def _setup_ui(self, initial_value: float):
        """Настройка интерфейса виджета."""
        # Минимальные размеры виджета
        self.setMinimumWidth(280)
        self.setMinimumHeight(40)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 4)
        layout.setSpacing(6)

        # Кнопка помощи слева
        self.help_button = QPushButton("?")
        self.help_button.setProperty("helpButton", True)
        self.help_button.setToolTip(self.tooltip_text)
        self.help_button.setCursor(Qt.WhatsThisCursor)
        self.help_button.setFocusPolicy(Qt.NoFocus)
        self.help_button.setFixedSize(26, 26)
        layout.addWidget(self.help_button)

        # Лейбл
        self.label = QLabel(self.label_text)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.label.setMinimumSize(120, 28)
        layout.addWidget(self.label)

        # Поле ввода справа
        min_val, max_val, decimals, step = self.config
        self.spinbox = QDoubleSpinBox()
        self.spinbox.setMinimum(min_val)
        self.spinbox.setMaximum(max_val)
        self.spinbox.setDecimals(int(decimals))
        self.spinbox.setSingleStep(step)
        self.spinbox.setValue(initial_value)
        self.spinbox.setAlignment(Qt.AlignRight)
        self.spinbox.setMinimumSize(100, 32)

        # Подключаем сигнал изменения значения
        self.spinbox.valueChanged.connect(self._on_value_changed)

        layout.addWidget(self.spinbox)

    def _on_value_changed(self, value: float):
        """Обработчик изменения значения."""
        self.valueChanged.emit(self.param_name, value)

    def value(self) -> float:
        """Получить текущее значение."""
        return self.spinbox.value()

    def setValue(self, value: float):
        """Установить значение."""
        self.spinbox.setValue(value)

    def setEnabled(self, enabled: bool):
        """Включить/выключить виджет."""
        self.spinbox.setEnabled(enabled)


class ParameterGroup(QWidget):
    """
    Группа параметров для секции интерфейса.
    Удобный способ создать несколько ParameterWidget.
    """

    valueChanged = Signal(str, float)

    def __init__(
        self,
        param_names: list[str],
        values: dict[str, float],
        parent: QWidget = None
    ):
        super().__init__(parent)

        self.widgets: dict[str, ParameterWidget] = {}
        self._setup_ui(param_names, values)

    def _setup_ui(self, param_names: list[str], values: dict[str, float]):
        """Настройка интерфейса группы."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)

        for name in param_names:
            value = values.get(name, 0.0)
            widget = ParameterWidget(name, value, self)
            widget.valueChanged.connect(self.valueChanged.emit)
            self.widgets[name] = widget
            layout.addWidget(widget)

        layout.addStretch()

    def get_values(self) -> dict[str, float]:
        """Получить все значения параметров."""
        return {name: widget.value() for name, widget in self.widgets.items()}

    def set_values(self, values: dict[str, float]):
        """Установить значения параметров."""
        for name, value in values.items():
            if name in self.widgets:
                self.widgets[name].setValue(value)

    def get_widget(self, param_name: str) -> ParameterWidget:
        """Получить виджет по имени параметра."""
        return self.widgets.get(param_name)
