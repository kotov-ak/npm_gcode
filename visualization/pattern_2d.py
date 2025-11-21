# -*- coding: utf-8 -*-
"""
Модуль создания 2D визуализации развёртки паттернов пробития для иглопробивного станка

Этот модуль создаёт 2D развёртку цилиндрической поверхности и отображает точки пробития
в прямоугольном окне размером needle_step_X × needle_step_Y (по умолчанию 8×8 мм).

Функции:
    - create_punch_visualization_2d(params, html_path): Создаёт 2D визуализацию развёртки
    - draw_2d_visualization(all_hits, params, nTurns, html_path): Отрисовка 2D графика

Развёртка цилиндра:
    - Ось X: осевая координата (needle_step_X мм)
    - Ось Y: окружная координата (дуга на поверхности цилиндра, развёрнутая в линию, needle_step_Y мм)
    - Преобразование: y_2d = theta * radius, где theta - угол в радианах

"""

import sys
import os

# Обеспечиваем корректный импорт при запуске модуля напрямую (до всех остальных импортов!)
if __name__ == "__main__":
    # Добавляем корневую директорию проекта в путь
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import plotly.graph_objects as go
import traceback

from functions.tube_command_generator import TubeCommandGenerator
from functions.motion_commands import MotionCommand, CommandType

# Импорт из локальных модулей визуализации
try:
    from .config import VisualizationConfig
    from .utils import validate_output_path, get_visualization_stats, log_visualization_stats
except ImportError:
    # Fallback для прямого запуска - импортируем visualization.* как модули
    from visualization.config import VisualizationConfig
    from visualization.utils import validate_output_path, get_visualization_stats, log_visualization_stats


def create_punch_visualization_2d(params: dict, html_path: str = "visualization_2d.html"):
    """
    Создает 2D визуализацию развёртки паттерна пробития на основе параметров

    Args:
        params (dict): Словарь параметров пробития
        html_path (str): Путь для сохранения HTML файла
    """
    try:
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Начало генерации визуализации с параметрами:")
        for key, value in params.items():
            print(f"[ВИЗУАЛИЗАЦИЯ 2D]   {key}: {value}")

        # Создаем генератор команд
        print("[ВИЗУАЛИЗАЦИЯ 2D] Создание генератора команд...")
        generator = TubeCommandGenerator(params)

        # Получаем количество оборотов из конфигурации
        volumetric_density = generator.config.VOLUMETRIC_DENSITY_MAP[params['volumetric_density']]
        revolutions = volumetric_density  # используем количество оборотов для полного паттерна
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] revolutions: {revolutions}")

        print("[ВИЗУАЛИЗАЦИЯ 2D] Генерация случайных смещений...")
        generator.generate_random_offsets(revolutions)

        print("[ВИЗУАЛИЗАЦИЯ 2D] Генерация команд...")
        commands = generator.generate_commands(revolutions)
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Сгенерировано команд: {len(commands)}")

        # Извлекаем координаты точек пробития (команды с комментарием "Подход к точке пробития")
        print("[ВИЗУАЛИЗАЦИЯ 2D] Извлечение координат точек пробития...")
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

                    # Сохраняем осевую координату и угол
                    x = cmd.x
                    theta = np.deg2rad(current_angle)

                    # Радиус для расчета развёртки
                    r = params['i_diam'] / 2.0

                    # Преобразование в координаты развёртки
                    # x остается как есть (осевая координата)
                    # y = arc_length = theta * radius (дуговая координата развернута в линейную)
                    x_2d = x
                    y_2d = theta * r

                    all_hits.append((x_2d, y_2d, turn_idx, theta, current_angle))

            except Exception as e:
                print(f"[ВИЗУАЛИЗАЦИЯ 2D] ОШИБКА при обработке команды {i}: {e}")
                print(f"[ВИЗУАЛИЗАЦИЯ 2D] Команда: {cmd}")
                traceback.print_exc()
                continue

        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Найдено команд подхода: {approach_count}")
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Извлечено точек пробития: {len(all_hits)}")

        if not all_hits:
            raise ValueError("Не найдено точек пробития для визуализации")

        # Рисуем визуализацию
        print("[ВИЗУАЛИЗАЦИЯ 2D] Создание 2D визуализации...")
        result_path = draw_2d_visualization(all_hits, params, revolutions, html_path)
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Визуализация успешно сохранена в: {html_path}")
        return result_path

    except Exception as e:
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] КРИТИЧЕСКАЯ ОШИБКА в create_punch_visualization_2d: {e}")
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] Тип ошибки: {type(e).__name__}")
        print("[ВИЗУАЛИЗАЦИЯ 2D] Полный стек ошибки:")
        traceback.print_exc()
        raise


def draw_2d_visualization(all_hits, params, nTurns, html_path="visualization_2d.html"):
    """
    Создает 2D визуализацию развёртки точек пробития в прямоугольнике needle_step_X × needle_step_Y

    Args:
        all_hits: Список координат точек пробития [(x_2d, y_2d, turn_idx, theta, angle_deg), ...]
        params: Параметры системы
        nTurns: Количество оборотов для отображения
        html_path: Путь для сохранения HTML файла
    """

    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Начало создания 2D визуализации...")
    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Количество точек: {len(all_hits)}")
    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Количество оборотов для отображения: {nTurns}")
    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Путь сохранения: {html_path}")

    if not all_hits:
        raise ValueError("Пустой список точек для визуализации")

    # Размеры прямоугольника развёртки
    needle_step_X = params['needle_step_X']
    needle_step_Y = params['needle_step_Y']

    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Размер окна развёртки: {needle_step_X} × {needle_step_Y} мм")

    # Проверяем выходной путь
    is_valid_path, error_msg = validate_output_path(html_path)
    if not is_valid_path:
        raise ValueError(f"Некорректный путь для сохранения: {error_msg}")

    # Фильтруем точки, которые попадают в прямоугольник развёртки
    # Прямоугольник: 0 <= x <= needle_step_X, 0 <= y <= needle_step_Y
    print("[ВИЗУАЛИЗАЦИЯ 2D] Фильтрация точек по прямоугольнику развёртки...")
    filtered_hits = []
    for x_2d, y_2d, turn_idx, theta, angle_deg in all_hits:
        # Нормализуем y_2d к диапазону [0, 2π*r) с помощью модуля по периметру окружности
        r = params['i_diam'] / 2.0
        circumference = 2 * np.pi * r
        y_2d_normalized = y_2d % circumference

        # Проверяем попадание в прямоугольник
        if 0 <= x_2d <= needle_step_X and 0 <= y_2d_normalized <= needle_step_Y:
            filtered_hits.append((x_2d, y_2d_normalized, turn_idx, theta, angle_deg))

    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Точек после фильтрации: {len(filtered_hits)}")

    if not filtered_hits:
        error_msg = (
            f"Нет точек в заданном окне развёртки "
            f"(0 <= x <= {needle_step_X} мм, 0 <= y <= {needle_step_Y} мм). "
            f"Проверьте параметры генерации или размеры окна."
        )
        print(f"[ВИЗУАЛИЗАЦИЯ 2D] ОШИБКА: {error_msg}")
        raise ValueError(error_msg)

    # Цвета для оборотов
    base_colors = VisualizationConfig.BASE_COLORS

    print("[ВИЗУАЛИЗАЦИЯ 2D] Создание фигуры plotly...")
    fig = go.Figure()

    # Добавляем три прямоугольника развёртки (левый, центральный, правый)
    # Левый прямоугольник
    fig.add_trace(go.Scatter(
        x=[-needle_step_X, 0, 0, -needle_step_X, -needle_step_X],
        y=[0, 0, needle_step_Y, needle_step_Y, 0],
        mode='lines',
        line=dict(color='lightgray', width=2, dash='dash'),
        name='Окно развёртки (левое)',
        showlegend=True
    ))

    # Центральный прямоугольник (основное окно)
    fig.add_trace(go.Scatter(
        x=[0, needle_step_X, needle_step_X, 0, 0],
        y=[0, 0, needle_step_Y, needle_step_Y, 0],
        mode='lines',
        line=dict(color='darkgray', width=2, dash='solid'),
        name='Окно развёртки (основное)',
        showlegend=True
    ))

    # Правый прямоугольник
    fig.add_trace(go.Scatter(
        x=[needle_step_X, 2 * needle_step_X, 2 * needle_step_X, needle_step_X, needle_step_X],
        y=[0, 0, needle_step_Y, needle_step_Y, 0],
        mode='lines',
        line=dict(color='lightgray', width=2, dash='dash'),
        name='Окно развёртки (правое)',
        showlegend=True
    ))

    # Добавляем серые точки (слева и справа)
    print("[ВИЗУАЛИЗАЦИЯ 2D] Добавление серых точек...")
    periodic_points_left = []
    periodic_points_right = []

    for x, y, _, _, _ in filtered_hits:
        periodic_points_left.append((x - needle_step_X, y))
        periodic_points_right.append((x + needle_step_X, y))

    # Добавляем левые серые точки
    if periodic_points_left:
        px_left, py_left = zip(*periodic_points_left)
        fig.add_trace(go.Scatter(
            x=px_left, y=py_left,
            mode='markers',
            marker=dict(
                size=VisualizationConfig.POINT_SIZE_2D,
                color='gray',
                opacity=0.5
            ),
            name='Периодичность (слева)',
            visible=True,
            showlegend=True,
        ))

    # Добавляем правые серые точки
    if periodic_points_right:
        px_right, py_right = zip(*periodic_points_right)
        fig.add_trace(go.Scatter(
            x=px_right, y=py_right,
            mode='markers',
            marker=dict(
                size=VisualizationConfig.POINT_SIZE_2D,
                color='gray',
                opacity=0.5
            ),
            name='Периодичность (справа)',
            visible=True,
            showlegend=True,
        ))

    print(f"[ВИЗУАЛИЗАЦИЯ 2D] Добавлено серых точек: {len(periodic_points_left) + len(periodic_points_right)}")

    # Теперь добавляем основные точки пробития по оборотам
    for turn in range(nTurns):
        pts = [(x, y) for x, y, t, th, a in filtered_hits if t == turn]
        if pts:
            px, py = zip(*pts)
            fig.add_trace(go.Scatter(
                x=px, y=py,
                mode='markers',
                marker=dict(
                    size=VisualizationConfig.POINT_SIZE_2D,
                    color=base_colors[turn % len(base_colors)],
                    opacity=VisualizationConfig.POINT_OPACITY
                ),
                name=f"Оборот {turn+1}",
                visible=True,
                legendgroup=f"turn{turn}",
            ))

    print("[ВИЗУАЛИЗАЦИЯ 2D] Настройка макета...")
    # Расширенная область: от -needle_step_X до 2*needle_step_X (3 окна по оси X)
    x_range = [-needle_step_X - 0.5, 2*needle_step_X + 0.5]
    y_range = [-0.5, needle_step_Y + 0.5]

    fig.update_layout(
        xaxis_title=f'X (осевая координата, мм)',
        yaxis_title=f'Y (окружная координата развёртки, мм)',
        xaxis=dict(
            range=x_range,
            scaleanchor="y",
            scaleratio=1  # Одинаковый масштаб по обеим осям
        ),
        yaxis=dict(
            range=y_range,
        ),
        legend_title="Слои",
        margin=VisualizationConfig.MARGIN,
        title=f"2D развёртка паттерна пробития ({needle_step_X} × {needle_step_Y} мм)",
        hovermode='closest'
    )

    print("[ВИЗУАЛИЗАЦИЯ 2D] Сохранение HTML файла...")
    # Сохранение в HTML
    fig.write_html(html_path,
                   include_plotlyjs=VisualizationConfig.INCLUDE_PLOTLYJS,
                   auto_open=True)
    print(f"[ВИЗУАЛИЗАЦИЯ 2D] HTML файл успешно сохранен")

    return html_path


if __name__ == "__main__":
    """
    Тестовый запуск 2D визуализации с конфигурацией по умолчанию
    """
    from constants.const import advanced_dict

    print("=" * 80)
    print("2D визуализации развёртки паттерна пробития с параметрами по умолчанию")
    print("=" * 80)

    # Используем параметры по умолчанию из const.py
    test_params = advanced_dict.copy()

    try:
        create_punch_visualization_2d(
            params=test_params,
            html_path="visualization_pattern_2d.html"
        )
        print("\n" + "=" * 80)
        print("✓ 2D визуализация успешно создана!")
        print("\n" + "=" * 80)
    except Exception as e:
        print("\n" + "=" * 80)
        print(f"✗ ОШИБКА при создании визуализации: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)
