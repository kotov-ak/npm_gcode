# -*- coding: utf-8 -*-
"""
Визуализация позиций игл иглопробивного станка

Отображает расположение игл в прямоугольном паттерне с регулярным шагом.
"""

import plotly.graph_objects as go
from typing import Tuple, List, Dict
import webbrowser
import sys
import os

# Для тестового запуска добавляем родительскую директорию в путь
if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from visualization.config import NeedleVisualizationConfig
else:
    from .config import NeedleVisualizationConfig


def calculate_needle_positions(
    needle_step_X: float,
    needle_step_Y: float,
    head_len: float,
    num_of_needle_rows: int
) -> Tuple[List[float], List[float], bool, str]:
    """
    Рассчитывает позиции игл в прямоугольном паттерне

    Args:
        needle_step_X: Расстояние между иглами вдоль оси X (мм)
        needle_step_Y: Расстояние между иглами вдоль оси Y (мм)
        head_len: Максимальная длина иглопробивной головки (мм)
        num_of_needle_rows: Количество рядов игл вдоль оси Y

    Returns:
        Tuple содержащий:
        - List[float]: X координаты игл
        - List[float]: Y координаты игл
        - bool: Флаг предупреждения (True если есть проблемы с делением)
        - str: Сообщение предупреждения (пустое если проблем нет)
    """
    x_positions = []
    y_positions = []
    warning = False
    warning_message = ""

    # Рассчитываем количество игл вдоль X
    # Между первой и последней иглой должно быть не более head_len
    # Если n игл, то между ними (n-1) промежутков
    # (n-1) * needle_step_X <= head_len
    # n <= head_len / needle_step_X + 1

    max_needles_X = int(head_len / needle_step_X) + 1
    total_distance_X = (max_needles_X - 1) * needle_step_X

    # Проверяем, делится ли нацело
    if abs(total_distance_X - head_len) > 0.001 and total_distance_X < head_len:
        # Проверяем, можем ли добавить еще одну иглу
        if (max_needles_X) * needle_step_X <= head_len + 0.001:
            max_needles_X += 1
            total_distance_X = (max_needles_X - 1) * needle_step_X

    # Проверяем корректность деления
    if abs(head_len - total_distance_X) > 0.001:
        warning = True
        warning_message = (
            f"⚠ ПРЕДУПРЕЖДЕНИЕ: head_len ({head_len} мм) не делится нацело на needle_step_X ({needle_step_X} мм).\n"
            f"Количество игл вдоль X: {max_needles_X}\n"
            f"Фактическое расстояние между первой и последней иглой: {total_distance_X:.2f} мм\n"
            f"Разница: {abs(head_len - total_distance_X):.2f} мм"
        )

    # Генерируем позиции игл
    # Начинаем с 0 по обеим осям
    for row in range(num_of_needle_rows):
        y = row * needle_step_Y
        for col in range(max_needles_X):
            x = col * needle_step_X
            x_positions.append(x)
            y_positions.append(y)

    return x_positions, y_positions, warning, warning_message


def create_needle_visualization(
    needle_step_X: float,
    needle_step_Y: float,
    head_len: float,
    num_of_needle_rows: int,
    output_file: str = "needle_positions.html",
    auto_open: bool = True,
    config: NeedleVisualizationConfig = None
) -> Tuple[go.Figure, bool, str]:
    """
    Создает визуализацию позиций игл в прямоугольном паттерне

    Args:
        needle_step_X: Расстояние между иглами вдоль оси X (мм)
        needle_step_Y: Расстояние между иглами вдоль оси Y (мм)
        head_len: Максимальная длина иглопробивной головки (мм)
        num_of_needle_rows: Количество рядов игл вдоль оси Y
        output_file: Путь к выходному HTML файлу
        auto_open: Автоматически открыть в браузере
        config: Конфигурация визуализации (опционально)

    Returns:
        Tuple содержащий:
        - go.Figure: Объект графика Plotly
        - bool: Флаг предупреждения
        - str: Сообщение предупреждения
    """
    if config is None:
        config = NeedleVisualizationConfig()

    # Рассчитываем позиции игл
    x_positions, y_positions, warning, warning_message = calculate_needle_positions(
        needle_step_X, needle_step_Y, head_len, num_of_needle_rows
    )

    if not x_positions:
        raise ValueError("Не удалось рассчитать позиции игл. Проверьте входные параметры.")

    # Определяем границы области расположения игл
    min_x = min(x_positions)
    max_x = max(x_positions)
    min_y = min(y_positions)
    max_y = max(y_positions)

    # Определяем границы прямоугольника с отступами
    rect_min_x = min_x - config.OFFSET_LEFT
    rect_max_x = max_x + config.OFFSET_RIGHT
    rect_min_y = min_y - config.OFFSET_BOTTOM
    rect_max_y = max_y + config.OFFSET_TOP

    # Создаем фигуру
    fig = go.Figure()

    # Добавляем внешний прямоугольник (с отступами)
    fig.add_trace(go.Scatter(
        x=[rect_min_x, rect_max_x, rect_max_x, rect_min_x, rect_min_x],
        y=[rect_min_y, rect_min_y, rect_max_y, rect_max_y, rect_min_y],
        mode='lines',
        line=dict(
            color=config.RECTANGLE_COLOR,
            width=config.RECTANGLE_LINE_WIDTH
        ),
        fill='toself',
        fillcolor=config.RECTANGLE_COLOR,
        opacity=config.RECTANGLE_OPACITY,
        name='Игольница',
        hoverinfo='skip'
    ))

    # Добавляем границу игольницы (точная область расположения игл)
    fig.add_trace(go.Scatter(
        x=[rect_min_x, rect_max_x, rect_max_x, rect_min_x, rect_min_x],
        y=[rect_min_y, rect_min_y, rect_max_y, rect_max_y, rect_min_y],
        mode='lines',
        line=dict(
            color=config.NEEDLE_BED_BORDER_COLOR,
            width=config.NEEDLE_BED_BORDER_WIDTH,
            dash='solid'
        ),
        name='Граница игольницы',
        hoverinfo='skip'
    ))

    # Добавляем точки игл
    fig.add_trace(go.Scatter(
        x=x_positions,
        y=y_positions,
        mode='markers',
        marker=dict(
            size=config.NEEDLE_POINT_SIZE,
            color=config.NEEDLE_COLOR,
            opacity=config.NEEDLE_OPACITY,
            line=dict(width=0.5, color='darkred')
        ),
        name='Иглы',
        hovertemplate='<b>Игла</b><br>' +
                      '<b>X:</b> %{x:.2f} мм<br>' +
                      '<b>Y:</b> %{y:.2f} мм<br>' +
                      '<extra></extra>'
    ))

    # Настройка макета
    title_text = f'Визуализация игольницы'
    if warning:
        title_text += ' ⚠ ПРЕДУПРЕЖДЕНИЕ'

    fig.update_layout(
        title=dict(
            text=title_text,
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title='X (мм)',
            showgrid=False,
            zeroline=False,
            showline=False
        ),
        yaxis=dict(
            title='Y (мм)',
            showgrid=False,
            zeroline=False,
            showline=False,
            scaleanchor='x',
            scaleratio=1
        ),
        plot_bgcolor='white',
        hovermode='closest',
        margin=config.MARGIN,
        showlegend=True,
        legend=dict(
            x=1.02,
            y=1,
            xanchor='left',
            yanchor='top'
        )
    )

    # Добавляем аннотацию с параметрами
    annotation_text = (
        f'<b>Параметры:</b><br>'
        f'Шаг по X: <b>{needle_step_X}</b> мм<br>'
        f'Шаг по Y: <b>{needle_step_Y}</b> мм<br>'
        f'Длина игольницы: <b>{head_len}</b> мм<br>'
        f'Рядов: <b>{num_of_needle_rows}</b><br>'
        f'Игл вдоль X: <b>{len(set(x_positions))}</b><br>'
        f'Всего игл: <b>{len(x_positions)}</b>'
    )

    fig.add_annotation(
        text=annotation_text,
        xref="paper", yref="paper",
        x=1.02, y=0.5,
        xanchor='left', yanchor='middle',
        showarrow=False,
        font=dict(size=11, family='Arial, sans-serif'),
        align='left',
        bgcolor='rgba(255, 255, 255, 0.9)',
        bordercolor='gray',
        borderwidth=1,
        borderpad=8
    )

    # Сохраняем в HTML
    fig.write_html(
        output_file,
        include_plotlyjs=config.INCLUDE_PLOTLYJS,
        config={'displayModeBar': True, 'displaylogo': False}
    )

    print(f"✓ Визуализация сохранена в: {output_file}")
    print(f"✓ Количество игл: {len(x_positions)}")
    if warning:
        print(warning_message)

    # Открываем в браузере
    if auto_open:
        webbrowser.open(output_file)

    return fig, warning, warning_message


# Тестовый запуск
if __name__ == "__main__":
    from constants.const import advanced_dict

    print("=" * 80)
    print("ТЕСТОВАЯ ВИЗУАЛИЗАЦИЯ ПОЗИЦИЙ ИГЛ")
    print("=" * 80)

    # Получаем параметры из advanced_dict
    needle_step_X = advanced_dict['needle_step_X']
    needle_step_Y = advanced_dict['needle_step_Y']
    head_len = advanced_dict['head_len']
    num_of_needle_rows = advanced_dict['num_of_needle_rows']

    print(f"\nПараметры:")
    print(f"  needle_step_X: {needle_step_X} мм")
    print(f"  needle_step_Y: {needle_step_Y} мм")
    print(f"  head_len: {head_len} мм")
    print(f"  num_of_needle_rows: {num_of_needle_rows}")
    print()

    # Создаем визуализацию
    fig, warning, warning_message = create_needle_visualization(
        needle_step_X=needle_step_X,
        needle_step_Y=needle_step_Y,
        head_len=head_len,
        num_of_needle_rows=num_of_needle_rows,
        output_file="needle_positions.html",
        auto_open=True
    )