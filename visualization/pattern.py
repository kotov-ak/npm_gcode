# -*- coding: utf-8 -*-
"""
Модуль создания 3D визуализации паттернов пробития для иглопробивного станка
"""

import numpy as np
import plotly.graph_objects as go
import traceback

from functions.tube_command_generator import TubeCommandGenerator
from functions.motion_commands import MotionCommand, CommandType
from .config import VisualizationConfig
from .utils import (
    validate_output_path, create_cylinder_surface,
    filter_points_by_turn, get_visualization_stats, log_visualization_stats
)


def create_punch_visualization(params: dict, html_path: str = "visualization.html"):
    """
    Создает визуализацию паттерна пробития на основе параметров

    Args:
        params (dict): Словарь параметров пробития
        html_path (str): Путь для сохранения HTML файла
    """
    try:
        print(f"[ВИЗУАЛИЗАЦИЯ] Начало генерации визуализации с параметрами:")
        for key, value in params.items():
            print(f"[ВИЗУАЛИЗАЦИЯ]   {key}: {value}")

        # Создаем генератор команд
        print("[ВИЗУАЛИЗАЦИЯ] Создание генератора команд...")
        generator = TubeCommandGenerator(params)

        # Получаем количество оборотов из конфигурации
        volumetric_density = generator.config.VOLUMETRIC_DENSITY_MAP[params['volumetric_density']]
        revolutions = volumetric_density  # используем количество оборотов для полного паттерна
        print(f"[ВИЗУАЛИЗАЦИЯ] revolutions: {revolutions}")

        print("[ВИЗУАЛИЗАЦИЯ] Генерация случайных смещений...")
        generator.generate_random_offsets(revolutions)

        print("[ВИЗУАЛИЗАЦИЯ] Генерация команд...")
        commands = generator.generate_commands(revolutions)
        print(f"[ВИЗУАЛИЗАЦИЯ] Сгенерировано команд: {len(commands)}")

        # Извлекаем координаты точек пробития (команды с комментарием "Подход к точке пробития")
        print("[ВИЗУАЛИЗАЦИЯ] Извлечение координат точек пробития...")
        all_hits = []
        turn_idx = 0
        current_angle = 0
        approach_count = 0
        previous_turn_angle = 0
        for i, cmd in enumerate(commands):
            try:
                if cmd.a is not None:  # Команда с поворотом
                    current_angle = cmd.a
                    # Проверяем, начался ли новый оборот (если угол уменьшился значительно)
                    if current_angle - previous_turn_angle >= 360.0:
                        previous_turn_angle += 360
                        turn_idx += 1

                # Ищем команды подхода по комментарию
                if (cmd.command_type == CommandType.LINEAR_MOVE and
                    cmd.comment == "Подход к точке пробития"):
                    approach_count += 1

                    # Применяем преобразование координат как в примере
                    x = cmd.x
                    theta = np.deg2rad(current_angle)

                    # На поверхности цилиндра, используем постоянный радиус i_diam/2
                    r = params['i_diam'] / 2.0

                    # Перевод в координаты цилиндра (ось вдоль X)
                    cx = x
                    cy = r * np.cos(theta)
                    cz = r * np.sin(theta)
                    all_hits.append((cx, cy, cz, turn_idx, theta))

            except Exception as e:
                print(f"[ВИЗУАЛИЗАЦИЯ] ОШИБКА при обработке команды {i}: {e}")
                print(f"[ВИЗУАЛИЗАЦИЯ] Команда: {cmd}")
                traceback.print_exc()
                continue

        print(f"[ВИЗУАЛИЗАЦИЯ] Найдено команд подхода: {approach_count}")
        print(f"[ВИЗУАЛИЗАЦИЯ] Извлечено точек пробития: {len(all_hits)}")

        if not all_hits:
            raise ValueError("Не найдено точек пробития для визуализации")

        # Рисуем визуализацию
        print("[ВИЗУАЛИЗАЦИЯ] Создание 3D визуализации...")
        draw_visualization(all_hits, params, revolutions, html_path)
        print(f"[ВИЗУАЛИЗАЦИЯ] Визуализация успешно сохранена в: {html_path}")

    except Exception as e:
        print(f"[ВИЗУАЛИЗАЦИЯ] КРИТИЧЕСКАЯ ОШИБКА в create_punch_visualization: {e}")
        print(f"[ВИЗУАЛИЗАЦИЯ] Тип ошибки: {type(e).__name__}")
        print("[ВИЗУАЛИЗАЦИЯ] Полный стек ошибки:")
        traceback.print_exc()
        raise


def draw_visualization(all_hits, params, nTurns, html_path="visualization.html"):
    """
    Создает 3D визуализацию точек пробития на цилиндре

    Args:
        all_hits: Список координат точек пробития [(x, y, z, turn_idx, theta), ...]
        params: Параметры системы
        nTurns: Количество оборотов для отображения
        html_path: Путь для сохранения HTML файла
    """

    print(f"[ВИЗУАЛИЗАЦИЯ] Начало создания 3D визуализации...")
    print(f"[ВИЗУАЛИЗАЦИЯ] Количество точек: {len(all_hits)}")
    print(f"[ВИЗУАЛИЗАЦИЯ] Количество оборотов для отображения: {nTurns}")
    print(f"[ВИЗУАЛИЗАЦИЯ] Путь сохранения: {html_path}")

    if not all_hits:
        raise ValueError("Пустой список точек для визуализации")

    StartDiameter = params["i_diam"]
    print(f"[ВИЗУАЛИЗАЦИЯ] Диаметр цилиндра: {StartDiameter}")

    # Геометрия цилиндра
    length = params['tube_len']
    print(f"[ВИЗУАЛИЗАЦИЯ] Длина цилиндра: {length}")

    # Проверяем выходной путь
    is_valid_path, error_msg = validate_output_path(html_path)
    if not is_valid_path:
        raise ValueError(f"Некорректный путь для сохранения: {error_msg}")

    # Получаем статистику точек
    stats = get_visualization_stats(all_hits)
    log_visualization_stats(stats)

    # Фильтруем точки для оптимизации производительности
    filtered_hits = filter_points_by_turn(all_hits, VisualizationConfig.MAX_DISPLAY_TURNS)
    if len(filtered_hits) < len(all_hits):
        print(f"[ВИЗУАЛИЗАЦИЯ] Отфильтровано точек для оптимизации: {len(all_hits)} -> {len(filtered_hits)}")
        all_hits = filtered_hits

    # Цвета для оборотов
    base_colors = VisualizationConfig.BASE_COLORS

    print("[ВИЗУАЛИЗАЦИЯ] Создание поверхности цилиндра...")
    # Создание поверхности цилиндра
    xgrid, y, z = create_cylinder_surface(StartDiameter, length, VisualizationConfig.CYLINDER_MESH_DENSITY)

    print("[ВИЗУАЛИЗАЦИЯ] Создание фигуры plotly...")
    fig = go.Figure()

    # Цилиндр
    fig.add_trace(go.Surface(
        x=xgrid, y=y, z=z,
        opacity=VisualizationConfig.CYLINDER_OPACITY,
        colorscale='gray', showscale=False,
        name="Цилиндр", showlegend=False
    ))

    print("[ВИЗУАЛИЗАЦИЯ] Добавление точек пробития...")
    for turn in range(nTurns):
        pts = [(x,y,z,th) for x,y,z,t,th in all_hits if t == turn]
        if pts:
            px, py, pz, ptheta = zip(*pts)
            fig.add_trace(go.Scatter3d(
                x=px, y=py, z=pz,
                mode='markers',
                marker=dict(
                    size=VisualizationConfig.POINT_SIZE,
                    color=base_colors[turn % len(base_colors)],
                    opacity=VisualizationConfig.POINT_OPACITY
                ),
                name=f"Оборот {turn+1}",
                visible=True,
                legendgroup=f"turn{turn}",
            ))

    print("[ВИЗУАЛИЗАЦИЯ] Настройка макета...")
    fig.update_layout(
        scene=dict(
            xaxis_title='X', yaxis_title='Y', zaxis_title='Z',
            aspectmode=VisualizationConfig.ASPECT_MODE
        ),
        legend_title="Слои",
        margin=VisualizationConfig.MARGIN,
        title="Визуализация паттерна пробития"
    )

    print("[ВИЗУАЛИЗАЦИЯ] Сохранение HTML файла...")
    # Сохранение в HTML
    fig.write_html(html_path,
                   include_plotlyjs=VisualizationConfig.INCLUDE_PLOTLYJS,
                   auto_open=True )
    print(f"[ВИЗУАЛИЗАЦИЯ] HTML файл успешно сохранен")

    return html_path