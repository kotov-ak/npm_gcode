import math
from typing import List, Union
from functions.motion_commands import MotionCommand


ACCEL_LINEAR = 300.0  # Ускорение для линейных осей (мм/с²)
ACCEL_ANGULAR = 300.0  # Ускорение для угловых осей (рад/с²)


def _time_for_move(d: float, v: float, a: float) -> float:
    """
    Расчет времени перемещения с учетом ускорения.

    Args:
        d (float): Расстояние в мм (или радианах для углов)
        v (float): Скорость в мм/с (или рад/с для углов)
        a (float): Ускорение в мм/с² (или рад/с² для углов)

    Returns:
        float: Время в секундах
    """
    if d <= 0 or v <= 0 or a <= 0:
        return 0.0

    # Расстояние разгона/торможения
    d_acc = (v * v) / a

    if d >= d_acc:
        # Трапецеидальный профиль скорости
        t_acc = v / a
        return 2.0 * t_acc + (d - d_acc) / v
    else:
        # Треугольный профиль скорости
        return 2.0 * math.sqrt(d / a)


def _seconds_to_dhms(s: float) -> str:
    """
    Конвертация секунд в формат 'дни часы:минуты:секунды'.

    Args:
        s (float): Время в секундах

    Returns:
        str: Время в формате "HH:MM:SS" или "N д HH:MM:SS"
    """
    s = int(round(s))
    days, s = divmod(s, 86400)
    h, s = divmod(s, 3600)
    m, s = divmod(s, 60)
    return f"{days} д {h:02d}:{m:02d}:{s:02d}" if days else f"{h:02d}:{m:02d}:{s:02d}"


def time_prediction_motioncommand(commands: List[MotionCommand]) -> List[List[Union[str, int]]]:
    """
    Функция расчета времени для MotionCommand.

    Args:
        commands (List[MotionCommand]): Список команд движения

    Returns:
        List[List[Union[str, int]]]: [[time_str_part1, time_sec_part1],
                                      [time_str_part2, time_sec_part2],
                                      [time_str_total, time_sec_total]]
    """
    if not commands:
        return [["0:00:00", 0], ["0:00:00", 0], ["0:00:00", 0]]

    # Поиск разделителя M110 (команда паузы для резки)
    split_idx = -1
    for i, cmd in enumerate(commands):
        if (cmd.command_type.value == "M" and
            cmd.m_code == 110):
            split_idx = i
            break

    if split_idx == -1:
        # Если нет разделителя, считаем все как одну часть
        total_time = _calculate_motion_time(commands)
        return [
            [_seconds_to_dhms(total_time), round(total_time)],
            ["0:00:00", 0],
            [_seconds_to_dhms(total_time), round(total_time)]
        ]

    # Разделение на части
    part1 = commands[:split_idx]
    part2 = commands[split_idx + 1:]

    # Расчет времени для частей
    t1 = _calculate_motion_time(part1)
    t2 = _calculate_motion_time(part2)
    total_time = t1 + t2

    return [
        [_seconds_to_dhms(t1), round(t1)],
        [_seconds_to_dhms(t2), round(t2)],
        [_seconds_to_dhms(total_time), round(total_time)]
    ]


def _calculate_motion_time(commands: List[MotionCommand]) -> float:
    """
    Расчет времени выполнения списка команд MotionCommand.

    Args:
        commands (List[MotionCommand]): Список команд

    Returns:
        float: Время выполнения в секундах
    """
    total_time = 0.0
    current_pos = {'x': 0.0, 'y': 0.0, 'z': 0.0, 'a': 0.0}

    for cmd in commands:
        if cmd.command_type.value == "G01":  # Линейное движение
            # Расчет линейного перемещения
            dx = (cmd.x - current_pos['x']) if cmd.x is not None else 0.0
            dy = (cmd.y - current_pos['y']) if cmd.y is not None else 0.0
            dz = (cmd.z - current_pos['z']) if cmd.z is not None else 0.0
            linear_distance = math.sqrt(dx*dx + dy*dy + dz*dz)

            # Расчет углового перемещения
            da = abs((cmd.a - current_pos['a']) if cmd.a is not None else 0.0)

            # Получение скорости
            feed_rate = cmd.feed_rate if cmd.feed_rate is not None else 1000.0

            # Время линейного движения
            if linear_distance > 0:
                linear_time = _time_for_move(linear_distance, feed_rate / 60.0, ACCEL_LINEAR)
                total_time += linear_time

            # Время углового движения (если только поворот без линейного движения)
            if da > 0 and linear_distance == 0:
                # Преобразуем угловую скорость в рад/сек (приблизительно)
                angular_speed = feed_rate / 60.0 * math.pi / 180.0  # рад/сек
                angular_distance = da * math.pi / 180.0  # рад
                angular_time = _time_for_move(angular_distance, angular_speed, ACCEL_ANGULAR)
                total_time += angular_time

            # Обновление текущей позиции
            if cmd.x is not None:
                current_pos['x'] = cmd.x
            if cmd.y is not None:
                current_pos['y'] = cmd.y
            if cmd.z is not None:
                current_pos['z'] = cmd.z
            if cmd.a is not None:
                current_pos['a'] = cmd.a

        elif cmd.command_type.value == "G04":  # Пауза
            if cmd.pause_time is not None:
                total_time += cmd.pause_time

        # M-коды в оценки времени пока не учитываются

    return total_time