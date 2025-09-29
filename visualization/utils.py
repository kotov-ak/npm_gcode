# -*- coding: utf-8 -*-
"""
Утилитарные функции для модуля визуализации
"""

import numpy as np
from typing import List, Tuple, Optional
import os
from .config import VisualizationConfig


def validate_output_path(html_path: str) -> Tuple[bool, str]:
    """
    Проверяет корректность пути для сохранения HTML файла.

    Args:
        html_path (str): Путь к файлу

    Returns:
        Tuple[bool, str]: (валидность, сообщение об ошибке)
    """
    try:
        # Проверяем, что директория существует
        directory = os.path.dirname(html_path)
        if directory and not os.path.exists(directory):
            return False, f"Директория не существует: {directory}"

        # Проверяем права на запись
        if directory:
            if not os.access(directory, os.W_OK):
                return False, f"Нет прав на запись в директорию: {directory}"

        # Проверяем расширение файла
        if not html_path.lower().endswith('.html'):
            return False, "Файл должен иметь расширение .html"

        return True, ""

    except Exception as e:
        return False, f"Ошибка проверки пути: {str(e)}"


def create_cylinder_surface(diameter: float, length: float, mesh_density: int = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Создает координаты поверхности цилиндра для визуализации.

    Args:
        diameter (float): Диаметр цилиндра
        length (float): Длина цилиндра
        mesh_density (int): Плотность сетки (количество точек по окружности)

    Returns:
        Tuple[np.ndarray, np.ndarray, np.ndarray]: Координаты X, Y, Z поверхности цилиндра
    """
    if mesh_density is None:
        mesh_density = VisualizationConfig.CYLINDER_MESH_DENSITY

    # Создание поверхности цилиндра
    theta = np.linspace(0, 2*np.pi, mesh_density)
    x = np.linspace(-length/2, length/2, 2)
    theta_mesh, xgrid = np.meshgrid(theta, x)
    y = (diameter/2.0) * np.cos(theta_mesh)
    z = (diameter/2.0) * np.sin(theta_mesh)

    return xgrid, y, z


def filter_points_by_turn(all_hits: List[Tuple], max_turns: int = None) -> List[Tuple]:
    """
    Фильтрует точки пробития по количеству оборотов для оптимизации производительности.

    Args:
        all_hits (List[Tuple]): Список всех точек пробития
        max_turns (int): Максимальное количество оборотов для отображения

    Returns:
        List[Tuple]: Отфильтрованный список точек
    """
    if max_turns is None:
        max_turns = VisualizationConfig.MAX_DISPLAY_TURNS

    if not all_hits:
        return []

    # Фильтруем точки по номеру оборота
    filtered_hits = [hit for hit in all_hits if hit[3] < max_turns]

    return filtered_hits


def get_visualization_stats(all_hits: List[Tuple]) -> dict:
    """
    Получает статистику по точкам визуализации.

    Args:
        all_hits (List[Tuple]): Список точек пробития

    Returns:
        dict: Словарь со статистикой
    """
    if not all_hits:
        return {
            'total_points': 0,
            'unique_turns': 0,
            'points_per_turn': {},
            'coordinate_ranges': {}
        }

    # Извлекаем данные
    x_coords = [hit[0] for hit in all_hits]
    y_coords = [hit[1] for hit in all_hits]
    z_coords = [hit[2] for hit in all_hits]
    turns = [hit[3] for hit in all_hits]

    # Считаем статистику по оборотам
    unique_turns = list(set(turns))
    points_per_turn = {turn: turns.count(turn) for turn in unique_turns}

    # Диапазоны координат
    coordinate_ranges = {
        'x': {'min': min(x_coords), 'max': max(x_coords)},
        'y': {'min': min(y_coords), 'max': max(y_coords)},
        'z': {'min': min(z_coords), 'max': max(z_coords)}
    }

    return {
        'total_points': len(all_hits),
        'unique_turns': len(unique_turns),
        'points_per_turn': points_per_turn,
        'coordinate_ranges': coordinate_ranges
    }


def log_visualization_stats(stats: dict, prefix: str = "[ВИЗУАЛИЗАЦИЯ]") -> None:
    """
    Выводит статистику визуализации в консоль.

    Args:
        stats (dict): Словарь статистики
        prefix (str): Префикс для логирования
    """
    if not VisualizationConfig.VERBOSE_LOGGING:
        return

    print(f"{prefix} === СТАТИСТИКА ВИЗУАЛИЗАЦИИ ===")
    print(f"{prefix} Общее количество точек: {stats['total_points']}")
    print(f"{prefix} Количество уникальных оборотов: {stats['unique_turns']}")

    if stats['points_per_turn']:
        print(f"{prefix} Точек по оборотам:")
        for turn, count in sorted(stats['points_per_turn'].items()):
            print(f"{prefix}   Оборот {turn}: {count} точек")

    if stats['coordinate_ranges']:
        print(f"{prefix} Диапазоны координат:")
        for axis, ranges in stats['coordinate_ranges'].items():
            print(f"{prefix}   {axis.upper()}: {ranges['min']:.3f} - {ranges['max']:.3f}")

    print(f"{prefix} === КОНЕЦ СТАТИСТИКИ ===")