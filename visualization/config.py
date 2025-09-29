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
    POINT_SIZE = 4
    POINT_OPACITY = 1.0

    # Настройки макета
    MARGIN = dict(l=0, r=0, t=30, b=0)
    ASPECT_MODE = 'data'

    # Настройки экспорта
    INCLUDE_PLOTLYJS = "cdn"  # Возможные значения: True, False, "cdn", "inline"

    # Факторы для осветления цветов
    LIGHTEN_FACTOR = 0.55

    # Максимальное количество оборотов для отображения (для производительности)
    MAX_DISPLAY_TURNS = 15

    # Настройки отладки
    DEBUG_MODE = False
    VERBOSE_LOGGING = True