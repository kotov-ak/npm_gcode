

import math as m
from datetime import datetime

import numpy as np

from functions.time_calc import *



def current_time():
    """
    Возвращает текущее время и дату в формате 'HH:MM:SS DD/MM/YYYY'.

    Returns:
        str: Строка с текущим временем и датой
    """
    return datetime.now().strftime("%H:%M:%S %d/%m/%Y")


def write_in_file_by_lines(lines, path):
    """
    Записывает список строк в файл, перезаписывая существующее содержимое.

    Args:
        lines (list): Список строк для записи
        path (str): Путь к файлу для записи

    Returns:
        bool: True если запись успешна, False при ошибке
    """
    try:
        with open(path, "w", encoding="utf-8") as file:
            file.writelines(lines)
        return True
    except IOError as e:
        print(f"Ошибка записи в файл {path}: {e}")
        return False


def split_by_lines(lines):
    """
    Добавляет символы новой строки к каждой строке в списке.

    Args:
        lines (list): Список строк (команд G-кода)

    Returns:
        list: Список строк с добавленными символами новой строки

    """
    return [line + '\n' for line in lines]




def check_params_for_validity(params_dict):
    """
    Проверка параметров на корректность значений и соблюдение технических требований.

    Args:
        params_dict (dict): Словарь с параметрами для проверки

    Returns:
        tuple: (bool, str, str) - (True/False, имя параметра, сообщение об ошибке)
        При успешной проверке: (True, None, None)
        При ошибке: (False, имя_параметра, сообщение_об_ошибке)
    """

    # Проверка на положительные и ненулевые значения
    for param_name, param_value in params_dict.items():
        if param_value <= 0:
            return False, param_name, f"Значение должно быть положительным числом (получено: {param_value})"
        if param_value == '':
            return False, param_name, "Значение не может быть пустым"

    # Проверка габаритных ограничений с подробными комментариями
    dimension_checks = [
        # (условие_ошибки, имя_параметра, сообщение_об_ошибке, допустимые_границы)
        (params_dict['tube_len'] >= 1200.001, 'tube_len',
         f"Длина трубы должна быть < 1200 мм (получено: {params_dict['tube_len']})"),

        (params_dict['i_diam'] <= 59.999, 'i_diam',
         f"Внутренний диаметр должен быть > 60 мм (получено: {params_dict['i_diam']})"),

        (params_dict['i_diam'] >= 300.001, 'i_diam',
         f"Внутренний диаметр должен быть < 300 мм (получено: {params_dict['i_diam']})"),

        (params_dict['o_diam'] >= 320.001, 'o_diam',
         f"Внешний диаметр должен быть < 320 мм (получено: {params_dict['o_diam']})"),

        (params_dict['o_diam'] <= 60.999, 'o_diam',
         f"Внешний диаметр должен быть > 61 мм (получено: {params_dict['o_diam']})"),

        (params_dict['i_diam'] > params_dict['o_diam'], 'i_diam',
         f"Внутренний диаметр ({params_dict['i_diam']}) не может быть больше внешнего ({params_dict['o_diam']})"),

        (params_dict['punch_step_r'] > params_dict['i_diam'] * 3.14, 'punch_step_r',
         f"Окружной шаг ({params_dict['punch_step_r']}) слишком большой для внутреннего диаметра {params_dict['i_diam']} мм"),

        (params_dict['punch_depth'] >= 15.001, 'punch_depth',
         f"Глубина пробития должна быть < 15 мм (получено: {params_dict['punch_depth']})"),

        (params_dict['idling_speed'] >= 7000.001, 'idling_speed',
         f"Скорость холостого хода должна быть < 7000 мм/мин (получено: {params_dict['idling_speed']})"),

        (params_dict['move_speed'] >= 2500.001, 'move_speed',
         f"Скорость пробития должна быть < 2500 мм/мин (получено: {params_dict['move_speed']})"),

        (params_dict['rotate_speed'] >= 2000.001, 'rotate_speed',
         f"Скорость поворота должна быть < 2000 мм/мин (получено: {params_dict['rotate_speed']})")
    ]

    for check_failed, param_name, error_message in dimension_checks:
        if check_failed:
            return False, param_name, f"{error_message}."

    # Проверка дискретных значений
    discrete_checks = [
        (params_dict['volumetric_density'] not in (15, 25, 45), 'volumetric_density',
         f"Объемная плотность должна быть 15, 25 или 45 (получено: {params_dict['volumetric_density']})"),

        (params_dict['punch_step_r'] not in (1, 2, 4), 'punch_step_r',
         f"Шаг пробития должен быть 1, 2 или 4 мм (получено: {params_dict['punch_step_r']})"),

        (params_dict['needle_step'] != 8, 'needle_step',
         f"Шаг игл должен быть равен 8 мм (получено: {params_dict['needle_step']})")
    ]

    for check_failed, param_name, error_message in discrete_checks:
        if check_failed:
            return False, param_name, f"{error_message}."

    # Все проверки пройдены успешно
    return True, None, None


def generate_values(x=0.0, b=0.25, n=None, seed=None):
    """
    Генерация n случайных значений в симметричном интервале [2*x - b, b].

    Используется для создания случайных смещений при пробитии, чтобы обеспечить
    равномерное покрытие и избежать регулярных паттернов.

    Args:
        x (float): Центр распределения. По умолчанию 0.0.
        b (float): Правая граница интервала. По умолчанию 0.25.
                   Левая граница вычисляется автоматически как 2*x - b.
        n (int): Количество генерируемых значений. Обязательный параметр.
        seed (int, optional): Seed для генератора случайных чисел для
                             воспроизводимости результатов. Если None,
                             seed генерируется случайно.

    Returns:
        tuple: (np.ndarray, int) -
               (массив сгенерированных значений, использованный seed)

    """

    # Генерация seed если не предоставлен
    if seed is None:
        seed = np.random.randint(0, 1000000)

    # Создаем генератор с конкретным seed
    rng = np.random.default_rng(seed)

    # Вычисляем левую границу интервала
    a = 2 * x - b

    # Генерируем n случайных значений в интервале [a, b]
    values = rng.uniform(a, b, size=n)

    return values, seed


def triangle_punch_radial_spiral_needle_full_random_upd(params_dict):
    """
    Генерация G-кода для пробития треугольного паттерна радиально-спиральным методом
    со случайными смещениями игл для равномерного покрытия.

    Алгоритм:
    1. Расчет общего количества слоев на основе разницы диаметров
    2. Для каждого слоя расчет оптимального количества сегментов
    3. Для каждого сегмента генерация команд перемещения и пробития
    4. Добавление случайных смещений для избежания регулярных паттернов

    Args:
        params_dict (dict): Словарь параметров пробития

    Returns:
        list: Список команд G-кода для станка
    """

    # ==================== КОНФИГУРАЦИЯ ====================
    DEBUG_OUTPUT = False  # Вывод отладочной информации в консоль
    DEBUG_TO_FILE = False  # Вывод отладочной информации в G-код
    EXTRA_ROTATIONS = 20  # Дополнительные обороты для запаса
    CENTER_X = 0.0  # Центр по оси X для случайных смещений

    # Соответствие объемной плотности к коэффициенту диаметров
    VOLUMETRIC_DENSITY_MAP = {15: 8, 25: 4, 45: 2}
    # ======================================================

    g_code_commands = []
    total_punches_actual = 0

    # ==================== РАСЧЕТ ОСНОВНЫХ ПАРАМЕТРОВ ====================
    # Получаем коэффициент на основе объемной плотности
    diam_coef = VOLUMETRIC_DENSITY_MAP[params_dict['volumetric_density']]

    # Расчет параметров намотки: разница диаметров и идеальное число оборотов
    diam_diff = params_dict['o_diam'] - params_dict['i_diam']
    ideal_rotation_num = diam_diff / (params_dict['fabric_thickness'] * 2)

    # Корректировка числа оборотов для полного паттерна
    rotation_delta = m.floor(ideal_rotation_num) % diam_coef
    if rotation_delta:
        main_rotation_num = m.floor(ideal_rotation_num) + diam_coef - rotation_delta
    else:
        main_rotation_num = m.floor(ideal_rotation_num)

    # Расчет реального внешнего диаметра с учетом намотки
    calculated_o_diam = params_dict['i_diam'] + main_rotation_num * params_dict['fabric_thickness'] * 2
    total_rotation_num = main_rotation_num + EXTRA_ROTATIONS

    total_fabric_len = 0

    if DEBUG_OUTPUT:
        print(f"Основные обороты: {main_rotation_num}, Всего оборотов: {total_rotation_num}")
        print(f"Рассчитанный внешний диаметр: {calculated_o_diam:.2f} мм")

    # ==================== ПРЕДВАРИТЕЛЬНЫЙ РАСЧЕТ ПРОБИТИЙ ====================
    total_cranks = 0
    for i in range(total_rotation_num):
        # Длина окружности текущего слоя
        current_diameter = params_dict['i_diam'] + 2 * params_dict['fabric_thickness'] * i
        circle_len = m.pi * current_diameter
        total_fabric_len+=circle_len
        # Расчет оптимального числа шагов для этой окружности
        ideal_steps = circle_len / params_dict['punch_step_r']
        steps_num_less = max(2, 2 * m.floor(ideal_steps / 2))
        steps_num_more = max(2, 2 * m.ceil(ideal_steps / 2))

        # Выбор лучшего варианта: минимальное отклонение шага
        steps_num_final = min((steps_num_less, steps_num_more),
                              key=lambda n: (abs(circle_len / n - params_dict['punch_step_r']), -n))
        total_cranks += steps_num_final

    # Расчет общего количества пробитий
    zones_per_crank = m.ceil(params_dict['tube_len'] / params_dict['punch_head_len'])
    punches_in_zone = round(params_dict['needle_step'] / diam_coef)
    total_punches = punches_in_zone * zones_per_crank * total_cranks

    # ==================== ГЕНЕРАЦИЯ СЛУЧАЙНЫХ СМЕЩЕНИЙ ====================
    generated_values_list, gen_seed = generate_values(
        x=CENTER_X,
        b=0.5,
        n=total_punches,
        seed=5  # Фиксированный seed для воспроизводимости
    )
    random_iterator = iter(generated_values_list)

    if DEBUG_OUTPUT:
        print(f"Всего пробитий рассчитано: {total_punches}")
        print(f"Seed для случайных смещений: {gen_seed}")

    # ==================== ФЛАГИ КОМПЕНСАЦИИ ДВИЖЕНИЯ ====================
    rev_zone_flag = 0  # Флаг обратного движения по зонам (0 → 1 → 0 → 1)
    rev_punch_flag = 0  # Флаг обратного движения по пробитиям (0 → 1 → 0 → 1)

    # ==================== ОСНОВНОЙ ЦИКЛ ГЕНЕРАЦИИ G-КОДА ====================
    for layer_idx in range(total_rotation_num):
        # Информация о текущем слое
        if DEBUG_TO_FILE:
            g_code_commands.append(f"; Слой {layer_idx + 1}/{total_rotation_num}")

        # Параметры текущего слоя
        current_diameter = params_dict['i_diam'] + 2 * params_dict['fabric_thickness'] * layer_idx
        circle_len = m.pi * current_diameter

        # Расчет оптимального числа шагов для этого слоя
        ideal_steps = circle_len / params_dict['punch_step_r']
        steps_num_less = max(2, 2 * m.floor(ideal_steps / 2))
        steps_num_more = max(2, 2 * m.ceil(ideal_steps / 2))

        steps_num_final = min((steps_num_less, steps_num_more),
                              key=lambda n: (abs(circle_len / n - params_dict['punch_step_r']), -n))
        step_size_final = round(circle_len / steps_num_final, 3)

        if DEBUG_TO_FILE:
            g_code_commands.append(f"; Диаметр: {current_diameter:.2f} мм, Шаг: {step_size_final:.3f} мм")

        # ЦИКЛ ПО СЕГМЕНТАМ (шагам поворота)
        for segment_idx in range(steps_num_final):
            if DEBUG_TO_FILE:
                g_code_commands.append(f"; Сегмент {segment_idx + 1}/{steps_num_final}")

            # Команда поворота - расчет угла и формирование G-кода
            rotate_angle = (step_size_final * 360) / circle_len
            total_angle = 360 * layer_idx + rotate_angle * segment_idx
            rotate_cmd = f"G01 A{round(total_angle, 3)} F{params_dict['rotate_speed']}"
            g_code_commands.append(rotate_cmd)

            # ЦИКЛ ПО ЗОНАМ (участкам вдоль трубы)
            for zone_idx in range(zones_per_crank):
                if DEBUG_TO_FILE:
                    g_code_commands.append(f"; Зона {zone_idx + 1}/{zones_per_crank}")

                # ЦИКЛ ПО ПРОБИТИЯМ (иглам в зоне)
                for punch_idx in range(punches_in_zone):
                    # ==================== РАСЧЕТ СМЕЩЕНИЙ ДЛЯ ТЕКУЩЕГО ПРОБИТИЯ ====================
                    # Смещение для сегмента (змейка - каждый второй сегмент смещен на половину шага)
                    segment_offset = (segment_idx % 2) * (params_dict['punch_step_r'] / 2)

                    # Смещение для слоя (сдвиг на каждом обороте)
                    layer_offset = (layer_idx % diam_coef) * params_dict['punch_step_r'] * (
                                params_dict['needle_step'] / diam_coef)

                    # Компенсация обратного движения (для змейкообразного паттерна)
                    rev_compensation_punch = (
                                round(params_dict['needle_step'] / diam_coef) - 1) if rev_punch_flag else 0
                    rev_compensation_zone = (zones_per_crank - 1) * params_dict[
                        'punch_head_len'] if rev_zone_flag else 0

                    # Случайное смещение для равномерного покрытия
                    random_offset = next(random_iterator)

                    # Смещение по Z для утолщения слоя (башмак)
                    if layer_idx + 1 <= main_rotation_num:
                        winding_offset_Z = params_dict['fabric_thickness'] * layer_idx
                    else:
                        winding_offset_Z = params_dict['fabric_thickness'] * main_rotation_num

                    # ==================== ФОРМИРОВАНИЕ КООРДИНАТ ====================
                    # Позиция по X: сумма всех смещений
                    x_position = (segment_offset + layer_offset +
                                  abs(params_dict['punch_step_r'] * punch_idx - rev_compensation_punch) +
                                  abs(params_dict['punch_head_len'] * zone_idx - rev_compensation_zone) +
                                  random_offset)

                    # Позиция по Y: учитывает толщину ткани (опускается с каждым слоем)
                    y_position = 0 - params_dict['fabric_thickness'] * layer_idx

                    # Позиция по Z: учитывает утолщение слоя для башмака
                    z_position = 0 - winding_offset_Z

                    # ==================== ГЕНЕРАЦИЯ КОМАНД G-КОДА ====================
                    # Команда подхода к точке пробития (холостой ход)
                    enter_move_cmd = f"G01 X{round(x_position, 3)} Y{round(y_position, 3)} Z{round(z_position, 3)} F{params_dict['idling_speed']}"

                    # Команда собственно пробития (рабочий ход)
                    punch_y = params_dict['punch_depth'] + params_dict['punch_offset'] - params_dict[
                        'fabric_thickness'] * layer_idx
                    punch_z = params_dict['shoe_depth'] - winding_offset_Z
                    punch_move_cmd = f"G01 X{round(x_position, 3)} Y{round(punch_y, 3)} Z{round(punch_z, 3)} F{params_dict['move_speed']}"

                    # Команда возврата из пробития (выход)
                    exit_move_cmd = f"G01 X{round(x_position, 3)} Y{round(y_position, 3)} Z{round(z_position, 3)} F{params_dict['move_speed']}"

                    # Добавляем все три команды в G-код
                    g_code_commands.append(enter_move_cmd)
                    g_code_commands.append(punch_move_cmd)
                    g_code_commands.append(exit_move_cmd)

                    total_punches_actual += 1

                    # ==================== ПРОВЕРКА НА ПОСЛЕДНЕЕ ПРОБИТИЕ ====================
                    # Если это последнее пробитие в основном режиме - добавляем команду паузы для резки
                    is_last_punch = (
                            punch_idx + 1 == punches_in_zone and
                            zone_idx + 1 == zones_per_crank and
                            segment_idx + 1 == steps_num_final and
                            layer_idx + 1 == main_rotation_num
                    )

                    if is_last_punch:
                        g_code_commands.append("M110 ; Пауза для резки")

            # ==================== ПЕРЕКЛЮЧЕНИЕ ФЛАГОВ ОБРАТНОГО ДВИЖЕНИЯ ====================
            # Инвертируем флаги для создания змейкообразного паттерна
            rev_zone_flag = 1 if rev_zone_flag == 0 else 0
            rev_punch_flag = 1 if rev_punch_flag == 0 else 0

    # ==================== ФИНАЛЬНАЯ ИНФОРМАЦИЯ ====================
    if DEBUG_OUTPUT:
        print(f"Всего пробитий сгенерировано: {total_punches_actual}")
        print(f"Рассчитано/Фактически: {total_punches}/{total_punches_actual}")



    comment_symbol = ';'
    info_lines = ['G-code has been generated based on ',
                  f'"{triangle_punch_radial_spiral_needle_full_random_upd.__name__}" function',
                  f'at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
                  '-' * 50,
                  'Approximate execution time:',
                  f'Part 1 => {time_prediction(g_code_commands)[0][0]} ({time_prediction(g_code_commands)[0][1]})',
                  f'Part 2 => {time_prediction(g_code_commands)[1][0]} ({time_prediction(g_code_commands)[1][1]})',
                  f'Total => {time_prediction(g_code_commands)[2][0]} ({time_prediction(g_code_commands)[2][1]})',
                  '-' * 50,
                  'Generation parameters:',
                  f'Tube length => {params_dict['tube_len']}',
                  f'Internal diameter => {params_dict['i_diam']}',
                  f'Outer diameter => {params_dict['o_diam']}',
                  f'Fabric thickness => {params_dict['fabric_thickness']}',
                  f'Punch step => {params_dict['punch_step_r']}',
                  f'Needles step => {params_dict['needle_step']}',
                  f'Volumetric density => {params_dict['volumetric_density']}',
                  f'Punch head len => {params_dict['punch_head_len']}',
                  f'Punch depth => {params_dict['punch_depth']}',
                  f'Shoe depth => {params_dict['shoe_depth']}',
                  f'Punch offset => {params_dict['punch_offset']}',
                  f'Idling speed => {params_dict['idling_speed']}',
                  f'Move_speed => {params_dict['move_speed']}',
                  f'Rotate_speed => {params_dict['rotate_speed']}',
                  '-' * 50,
                  'Additional calculated parameters:',
                  f'Calculated diameter => {calculated_o_diam}',
                  f'Main rotation number => {main_rotation_num}',
                  f'Fabric length => {round(total_fabric_len)}',
                  f'Total punch number => {total_punches}',
                  f'Seed for random => {gen_seed}',
                  '#'*50]
    info_lines[:] = [comment_symbol + x for x in info_lines]

    g_code_commands[:0] = info_lines

    # Преобразуем список команд в список строк с переносами
    return split_by_lines(g_code_commands)












# import math as m
# from datetime import datetime
#
# import numpy as np
#
# from constants.const import data_mode_dict, punch_mode_dict
#
#
# def current_time():
#     """'Снимок' текущего времени и даты"""
#
#     return str(datetime.now().strftime("%H:%M:%S %d/%m/%Y"))
#
#
# def write_in_file_by_lines(line, path):
#     """Запись (перезапись) в файл построчно"""
#
#     with open(path, "w") as file:
#         file.writelines(line)
#     return 0
#
#
# def check_params_for_validity(params_dict):
#     """Проверка параметров на 'здравый смысл'. Проверка корректности значений"""
#
#     # НУЖНО ПЕРЕОСМЫСЛИТЬ
#     # проверка на положительные и ненулевые значения
#     for i in params_dict.keys():
#         if (params_dict[i] <= 0 or
#                 params_dict[i] <= 0.0 or
#                 params_dict[i] == ''):
#             return False
#         else:
#             pass
#     # проверка на габаритные ограничения
#     # длина трубы
#     if params_dict['tube_len'] >= 1200.001:
#         return False
#     # внутренний диаметр
#     elif params_dict['i_diam'] <= 59.999 or params_dict['i_diam'] >= 300.001:
#         return False
#     # внешний диаметр
#     elif params_dict['o_diam'] >= 301.001 or params_dict['o_diam'] <= 60.999:
#         return False
#     # внешний и внутренний диаметры
#     elif params_dict['i_diam'] > params_dict['o_diam']:
#         return False
#     # окружной шаг
#     elif params_dict['punch_step_r'] > params_dict['i_diam'] * 3.14:
#         return False
#     # глубина пробития
#     elif params_dict['punch_depth'] >= 15.001:
#         return False
#     # скорость холостая пробития
#     elif params_dict['idling_speed'] >= 5000.001:
#         return False
#     # скорость пробития
#     elif params_dict['move_speed'] >= 2000.001:
#         return False
#     # скорость поворота
#     elif params_dict['rotate_speed'] >= 2000.001:
#         return False
#     # плотность пробития объемная поворота
#     elif params_dict['volumetric_density'] not in (15, 25, 45):
#         return False
#     # шаг пробития
#     elif params_dict['punch_step_r'] not in (1, 2, 4):
#         return False
#     # шаг пробития
#     elif params_dict['needle_step'] != 8:
#         return False
#     else:
#         return True
#
#
# def get_gen_type(punch_mode, data_mode):
#     """Определение кода режима"""
#
#     gen_code_list = [punch_mode_dict[punch_mode], data_mode_dict[data_mode]]
#     gen_code = int(''.join(map(str, gen_code_list)))
#
#     return gen_code
#
#
# def generate_values(x=0, b=0.25, n=None, seed=None):
#     if n is None:
#         raise ValueError("Нужно указать количество генераций (n)")
#
#     if seed is None:
#         seed = np.random.randint(0, 101)
#
#     rng = np.random.default_rng(seed)
#
#     # нижняя граница симметрично
#     a = 2 * x - b
#
#     values = rng.uniform(a, b, size=n)
#
#     return values, seed
#
#
# def split_by_lines(lines):
#     """Разбивка текса на строки"""
#
#     list_of_lines = [line + '\n' for line in lines]
#     return list_of_lines
#
#
# def triangle_punch_radial_spiral_needle_full_random_upd(params_dict):
#     """
#         Функция генерации пробития паттерна треугольника
#         Основание треугольника в паттерне варьируется (1, 2, 4) мм : punch_step_r
#         Задействован 1 ряд игл с шагом 8 мм : needle_step=8,
#         Учитывается "наслоение" ткани
#     """
#
#     # флаги для вывода доп информации
#     assistive_info_out = False
#     assistive_info_to_file = False
#
#     # массив для команд g-кода
#     g_code_commands = []
#     nop=0
#     # параметры по намотке
#     # длина ткани
#     fabric_len = 0
#     # количество пробитий
#     punch_count = 0
#     # количество проворотов
#     crank_count = 0
#
#     # флаги компенсации обратного движения
#     rev_zone_flag = 0
#     rev_punch_flag = 0
#
#     volumetric_density_dict = {
#         15: 8,
#         25: 4,
#         45: 2
#     }
#
#     volumetric_density = volumetric_density_dict[params_dict['volumetric_density']]
#
#     # корректировка внешнего диаметра
#     # коэффициент диаметров (количество оборотов на 1 паттерн)
#     diam_coef = volumetric_density  # в идеале надо задать параметрически (сейчас 4 исходя из 25 засечек на слой)
#     # разница в диаметрах (объем намотки)
#     diam_diff = params_dict['o_diam'] - params_dict['i_diam']
#     # идеальное число оборотов для формирования диаметра
#     ideal_rotation_num = diam_diff / (params_dict['fabric_thickness'] * 2)
#     # разница в оборотах до полного паттерна
#     rotation_delta = m.floor(ideal_rotation_num) % diam_coef
#     # вычисленное число оборотов (с учетом паттерна и диаметра)
#     main_rotation_num = round(m.floor(ideal_rotation_num) + diam_coef - rotation_delta if rotation_delta
#                               else m.floor(ideal_rotation_num))
#     # реальный (вычисленный) внешний диаметр
#     calculated_o_diam = params_dict['i_diam'] + main_rotation_num * params_dict['fabric_thickness'] * 2
#     print(calculated_o_diam)
#
#     extra_rotation_num = 20
#
#     total_rotation_num = main_rotation_num + extra_rotation_num
#
#     total_cranks = 0
#
#     for i in range(total_rotation_num):
#         circle_len = m.pi * (params_dict['i_diam'] + 2 * params_dict['fabric_thickness'] * i)
#         # «Идеальное» дробное число шагов
#         ideal_steps = circle_len / params_dict['punch_step_r']
#         # ближайшее чётное «большее» и «меньшее» (минимальный шаг 2)
#         steps_num_less = max(2, 2 * m.floor(ideal_steps / 2))
#         steps_num_more = max(2, 2 * m.ceil(ideal_steps / 2))
#         # Выбор лучшего: варианта: первично — минимальное отклонение, при равенстве — большее число шагов
#         steps_num_final = min((steps_num_less, steps_num_more),
#                               key=lambda n: (abs(circle_len / n - params_dict['punch_step_r']), -n))
#         total_cranks += steps_num_final
#
#     zones_per_crank = m.ceil((params_dict['tube_len'] / params_dict['punch_head_len']))
#     punches_in_zone = round(params_dict['needle_step'] / volumetric_density)
#     total_punches = punches_in_zone * zones_per_crank * total_cranks
#
#     generated_values_list, gen_seed = generate_values(x=0, b=0.5, n=total_punches, seed=5)
#     random_i = iter(generated_values_list)
#
#     for i in range(total_rotation_num):
#
#         # дополнительная информация
#         if assistive_info_out:
#             print(f';Layer {i + 1} of {total_rotation_num}')
#         if assistive_info_to_file:
#             g_code_commands.append(f';Layer {i + 1} of {total_rotation_num}')
#
#         # длина окружности
#         circle_len = m.pi * (params_dict['i_diam'] + 2 * params_dict['fabric_thickness'] * i)
#         # «Идеальное» дробное число шагов
#         ideal_steps = circle_len / params_dict['punch_step_r']
#         # ближайшее чётное «большее» и «меньшее» (минимальный шаг 2)
#         steps_num_less = max(2, 2 * m.floor(ideal_steps / 2))
#         steps_num_more = max(2, 2 * m.ceil(ideal_steps / 2))
#         # Выбор лучшего: варианта: первично — минимальное отклонение, при равенстве — большее число шагов
#         steps_num_final = min((steps_num_less, steps_num_more),
#                               key=lambda n: (abs(circle_len / n - params_dict['punch_step_r']), -n))
#         # округление шага
#         step_size_final = round(circle_len / steps_num_final, 3)
#
#         # параметры намотки
#         # прибавка длины ткани
#         if i + 1 <= main_rotation_num:
#             fabric_len += round(circle_len, 3)
#         # прибавка количества проворотов
#         crank_count += steps_num_final
#
#         # дополнительная информация
#         if assistive_info_out:
#             print(f'Заданный шаг: {params_dict['punch_step_r']}')
#             print(f'Реальный шаг: {step_size_final}')
#         if assistive_info_to_file:
#             g_code_commands.append(f'Required step: {params_dict['punch_step_r']}')
#             g_code_commands.append(f'Real (calculated) step: {step_size_final}')
#
#         if i + 1 <= main_rotation_num:
#             if assistive_info_out:
#                 print(f'Заданный внешний диаметр: {params_dict['o_diam']}')
#                 print(f'Реальный внешний диаметр: {calculated_o_diam}')
#             if assistive_info_to_file:
#                 g_code_commands.append(f'Required outer diameter: {params_dict['o_diam']}')
#                 g_code_commands.append(f'Real outer diameter: {calculated_o_diam}')
#
#         for j in range(steps_num_final):
#
#             # дополнительная информация
#             if assistive_info_out:
#                 print(f';Segment {j + 1} of {steps_num_final}')
#             if assistive_info_to_file:
#                 g_code_commands.append(f';Segment {j + 1} of {steps_num_final}')
#
#             # угол проворота
#             rotate_angle = (step_size_final * 360) / circle_len
#             # формирование команды g-кода
#             j_control_msg = f'G01 A{round(360 * i + rotate_angle * j, 3)} F{params_dict['rotate_speed']}'
#             g_code_commands.append(j_control_msg)
#
#             for k in range(m.ceil((params_dict['tube_len'] / params_dict['punch_head_len']))):
#
#                 # дополнительная информация
#                 if assistive_info_out:
#                     print(f';Zone {k + 1} of {m.ceil(params_dict['tube_len'] / params_dict['punch_head_len'])}')
#                 if assistive_info_to_file:
#                     g_code_commands.append(
#                         f';Zone {k + 1} of {m.ceil(params_dict['tube_len'] / params_dict['punch_head_len'])}')
#
#                 # пробитие в зоне (НАДО уточнить алгоритм)
#                 # Надо завязать параметры количества ударов, секций и оборотов  (слоев)
#                 section_num = volumetric_density
#                 punch_in_zone = round(params_dict['needle_step'] / volumetric_density)
#
#                 for l in range(punch_in_zone):
#
#                     if assistive_info_out:
#                         print(f';Section {l + 1} of {punch_in_zone}')
#                     if assistive_info_to_file:
#                         g_code_commands.append(f';Section {l + 1} of {punch_in_zone}')
#
#                     # смещение для сегмента (каждый проворот смещение "змейкой")
#                     segment_offset_flag = j % 2
#                     segment_offset_value = params_dict['punch_step_r'] / 2
#                     segment_offset = segment_offset_flag * segment_offset_value
#
#                     # смещение для слоя (каждый полный оборот)
#                     layer_offset_flag = i % round(section_num)
#                     layer_offset_value = params_dict['punch_step_r'] * (params_dict['needle_step'] / section_num)
#                     layer_offset = layer_offset_flag * layer_offset_value
#
#                     # смещение
#                     section_zone_offset = params_dict['punch_step_r']
#
#                     # компенсация обратного движения
#                     rev_val_punch = ((round(params_dict['needle_step'] / section_num) - 1)
#                                      if rev_punch_flag else 0)
#                     rev_val_zone = ((m.ceil((params_dict['tube_len'] / params_dict['punch_head_len']) - 1)
#                                      * params_dict['punch_head_len']
#                                      if rev_zone_flag else 0))
#
#                     random_offset_value = next(random_i)
#
#                     # смещение на утолщение слоя для башмака (Z)
#                     winding_offset_Z = (params_dict['fabric_thickness'] * i if i + 1 <= main_rotation_num
#                                         else params_dict['fabric_thickness'] * main_rotation_num)
#
#                     #  задание строк со значениями
#                     enter_move_cmd = (
#                         f'G01 X{round(segment_offset +
#                                       layer_offset +
#                                       abs(section_zone_offset * l - rev_val_punch) +
#                                       abs(params_dict['punch_head_len'] * k - rev_val_zone) +
#                                       random_offset_value, 3)} '
#                         f'Y{round(0 - params_dict['fabric_thickness'] * i, 3)} '
#                         f'Z{round(0 - winding_offset_Z, 3)} '
#                         f'F{params_dict['idling_speed']}')
#
#                     punch_move_cmd = (
#                         f'G01 X{round(segment_offset +
#                                       layer_offset +
#                                       abs(section_zone_offset * l - rev_val_punch) +
#                                       abs(params_dict['punch_head_len'] * k - rev_val_zone) +
#                                       random_offset_value, 3)} '
#                         f'Y{round(params_dict['punch_depth'] + params_dict['punch_offset'] - params_dict['fabric_thickness'] * i, 3)} '
#                         f'Z{round(params_dict['shoe_depth'] - winding_offset_Z, 3)} '
#                         f'F{params_dict['move_speed']}')
#
#                     exit_move_cmd = (
#                         f'G01 X{round(segment_offset +
#                                       layer_offset +
#                                       abs(section_zone_offset * l - rev_val_punch) +
#                                       abs(params_dict['punch_head_len'] * k - rev_val_zone) +
#                                       random_offset_value, 3)} '
#                         f'Y{round(0 - params_dict['fabric_thickness'] * i, 3)} '
#                         f'Z{round(0 - winding_offset_Z, 3)} '
#                         f'F{params_dict['move_speed']}')
#
#                     g_code_commands.append(enter_move_cmd)
#                     g_code_commands.append(punch_move_cmd)
#                     g_code_commands.append(exit_move_cmd)
#
#                     # плюс пробитие
#                     punch_count += 1
#
#                     if (l + 1 == punch_in_zone and
#                             k + 1 == m.ceil((params_dict['tube_len'] / params_dict['punch_head_len'])) and
#                             j + 1 == steps_num_final and
#                             i + 1 == main_rotation_num):
#                         print("Pause for cut")
#                         split_command = f'M110'
#                         g_code_commands.append(split_command)
#                         print(g_code_commands[-1])
#                         print('Inserted')
#                     nop+=1
#             # переключаем флаг (0→1, 1→0)
#             rev_zone_flag ^= 1
#             rev_punch_flag ^= 1
#
#     print(nop)
#     print(f'TTL_P: {total_punches}')
#     return split_by_lines(g_code_commands)
