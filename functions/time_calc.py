# -*- coding: utf-8 -*-
"""
Универсальная функция time_prediction() работает ТОЛЬКО для данных с разделителем SPLIT_CMD.
Принимает: путь к файлу ИЛИ массив команд.
Если разделитель не найден - возвращает ошибку.
"""

import re
import math
from typing import List, Optional, Any

# Настройки
SPLIT_CMD = "M110"
ACCEL_LINEAR = 300.0
ACCEL_ANGULAR = 300.0


def _time_for_move(d: float, v: float, a: float) -> float:
    """Расчет времени перемещения."""
    if d <= 0 or v <= 0 or a <= 0:
        return 0.0

    d_acc = (v * v) / a
    if d >= d_acc:
        t_acc = v / a
        return 2.0 * t_acc + (d - d_acc) / v
    else:
        return 2.0 * math.sqrt(d / a)


def _seconds_to_dhms(s: float) -> str:
    """Конвертация секунд в формат с днями."""
    s = int(round(s))
    days, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{days} д {h:02d}:{m:02d}:{s:02d}" if days else f"{h:02d}:{m:02d}:{s:02d}"


def _parse_commands(commands: List[str], start_pos: Optional[dict] = None) -> tuple:
    """Парсинг команд и расчет времени."""
    pos = {'X': 0.0, 'Y': 0.0, 'Z': 0.0, 'A': 0.0}
    if start_pos:
        pos.update(start_pos)

    total = 0.0

    for cmd in commands:
        # Очистка команды
        clean = cmd.split(';')[0].strip().upper()
        clean = re.sub(r'\(.*?\)', '', clean).strip()

        if not clean or not clean.startswith(('G0', 'G1')):
            continue

        # Извлечение параметров
        tokens = re.findall(r'([XYZAF])([-+]?\d*\.?\d+)', clean)
        feed = None
        targets = {}

        for axis, val in tokens:
            num = float(val)
            if axis == 'F':
                feed = num
            elif axis in pos:
                targets[axis] = num

        if feed is None:
            continue

        speed = feed / 60.0
        times = []

        # Расчет времени для линейных осей
        for axis in 'XYZ':
            dist = abs(targets.get(axis, pos[axis]) - pos[axis])
            times.append(_time_for_move(dist, speed, ACCEL_LINEAR))

        # Расчет времени для оси A
        dist_a = abs(targets.get('A', pos['A']) - pos['A'])
        times.append(_time_for_move(dist_a, speed, ACCEL_ANGULAR))

        total += max(times)
        pos.update(targets)

    return total, pos


def _find_split(commands: List[str]) -> int:
    """Поиск разделителя."""
    for i, cmd in enumerate(commands):
        clean = cmd.split(';')[0].strip().upper()
        if SPLIT_CMD.upper() in clean.split():
            return i
    return -1


def time_prediction(data) -> list[list[str | Any]]:
    """
    Универсальная функция расчета времени.
    Принимает: путь к файлу (str) или массив команд (list).
    """
    # Преобразование в массив команд
    if isinstance(data, str):
        with open(data, 'r', encoding='utf-8', errors='ignore') as f:
            commands = [line.strip() for line in f if line.strip()]
    elif isinstance(data, list):
        commands = data
    else:
        return "ОШИБКА: Неподдерживаемый тип данных"

    # Поиск разделителя
    split_idx = _find_split(commands)
    if split_idx == -1:
        return f"ОШИБКА: Не содержит разделитель '{SPLIT_CMD}'"

    # Расчет общего времени
    total_time, _ = _parse_commands(commands)

    # Разделение на части
    part1 = commands[:split_idx]
    part2 = commands[split_idx + 1:]

    # Расчет времени для частей
    t1, pos1 = _parse_commands(part1)
    t2, _ = _parse_commands(part2, pos1)

    # Формирование отчета
    return [[_seconds_to_dhms(t1), round(t1)],
            [_seconds_to_dhms(t2), round(t2)],
            [_seconds_to_dhms(total_time), round(total_time)]]
