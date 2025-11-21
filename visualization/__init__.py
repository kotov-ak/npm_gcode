# -*- coding: utf-8 -*-
"""
Модуль визуализации паттернов пробития для иглопробивного станка

Содержит функции для создания 3D и 2D визуализации точек пробития с использованием библиотеки plotly.

Модули:
    visualization: 3D визуализация точек пробития на цилиндрической поверхности
    visualization_2d: 2D визуализация развёртки цилиндрической поверхности
    config: Конфигурационные параметры визуализации
    utils: Утилитарные функции
"""

from .pattern import create_punch_visualization
from .pattern_2d import create_punch_visualization_2d
from .needle_positions import create_needle_visualization, calculate_needle_positions

__all__ = [
    'create_punch_visualization',
    'create_punch_visualization_2d',
    'create_needle_visualization',
    'calculate_needle_positions',
]

__version__ = '1.1.0'