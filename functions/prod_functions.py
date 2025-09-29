

from datetime import datetime

from functions.parameter_validator import ParameterValidator
from functions.advanced_punch_generator import CommandLinesGenerator
from functions.time_calc import time_prediction_motioncommand


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
    Обертка для нового класса ParameterValidator для сохранения совместимости.

    Args:
        params_dict (dict): Словарь с параметрами для проверки

    Returns:
        tuple: (bool, str, str) - (True/False, имя параметра, сообщение об ошибке)
    """
    validator = ParameterValidator()
    return validator.validate_all_parameters(params_dict)


# def triangle_punch_radial_spiral_needle_full_random_upd(params_dict):
#     """
#     Функция-обертка для сохранения совместимости с новой системой генерации.

#     Args:
#         params_dict (dict): Словарь параметров для генерации G-кода

#     Returns:
#         list: Список строк G-кода
#     """
#     generator = CommandLinesGenerator(params_dict)
#     return generator.generate_radial_spiral_pattern()

def calculate_execution_time(params_dict):
    """
    Расчет времени выполнения G-кода без генерации файла.
    Использует оптимизированную функцию для MotionCommand.

    Args:
        params_dict (dict): Словарь параметров для генерации G-кода

    Returns:
        list: [[time_str_part1, time_sec_part1], [time_str_part2, time_sec_part2], [time_str_total, time_sec_total]]
    """
    generator = CommandLinesGenerator(params_dict)
    commands = generator.generate_commands_only()
    return time_prediction_motioncommand(commands)