# -*- coding: utf-8 -*-
"""
Модуль визуализации паттернов пробития для иглопробивного станка

Содержит функции для создания 3D визуализации точек пробития на цилиндрической поверхности
с использованием библиотеки plotly.

Модули:
    visualization: Основные функции для создания визуализации
"""

from .visualization import create_punch_visualization

__all__ = [
    'create_punch_visualization',
]

__version__ = '1.0.0'