# -*- coding: utf-8 -*-
"""
Конфигурация для модуля визуализации
"""

# Настройки визуализации
class VisualizationConfig:
    """Конфигурационные параметры для визуализации"""

    # Цвета для различных оборотов/слоев
    BASE_COLORS = [
        "#e6194b", "#3cb44b", "#ffe119", "#4363d8", "#f58231",
        "#911eb4", "#46f0f0", "#f032e6", "#bcf60c", "#fabebe",
        "#008080", "#e6beff", "#9a6324", "#fffac8", "#800000"
    ]

    # Настройки цилиндра
    CYLINDER_OPACITY = 0.2
    CYLINDER_MESH_DENSITY = 60  # Количество точек для создания поверхности цилиндра

    # Настройки точек пробития
    POINT_SIZE = 4  # Размер точек для 3D визуализации
    POINT_SIZE_2D = 40  # Размер точек для 2D визуализации (развёртка)
    POINT_OPACITY = 1.0

    # Настройки макета
    MARGIN = dict(l=0, r=0, t=30, b=0)
    ASPECT_MODE = 'data'

    # Настройки экспорта
    INCLUDE_PLOTLYJS = True  # Возможные значения: True, False, "cdn", "inline" True для оффлайн работы

    # Факторы для осветления цветов
    LIGHTEN_FACTOR = 0.55

    # Максимальное количество оборотов для отображения (для производительности)
    MAX_DISPLAY_TURNS = 15

    # Настройки отладки
    DEBUG_MODE = False
    VERBOSE_LOGGING = True


class NeedleVisualizationConfig:
    """Конфигурационные параметры для визуализации позиций игл"""

    # Отступы прямоугольника от области расположения игл
    OFFSET_LEFT = 6.0   # мм, отступ слева
    OFFSET_RIGHT = 6.0  # мм, отступ справа
    OFFSET_TOP = 6.0    # мм, отступ сверху
    OFFSET_BOTTOM = 6.0 # мм, отступ снизу

    # Настройки отображения
    NEEDLE_POINT_SIZE = 8  # Размер точки иглы
    NEEDLE_COLOR = "#e6194b"  # Цвет точек игл
    NEEDLE_OPACITY = 1.0

    RECTANGLE_COLOR = "#4363d8"  # Цвет рамки прямоугольника
    RECTANGLE_OPACITY = 0.3
    RECTANGLE_LINE_WIDTH = 2

    NEEDLE_BED_BORDER_COLOR = "darkblue"  # Цвет границы игольницы
    NEEDLE_BED_BORDER_WIDTH = 2

    # Настройки макета
    MARGIN = dict(l=50, r=50, t=50, b=50)

    # Настройки экспорта
    INCLUDE_PLOTLYJS = "cdn"