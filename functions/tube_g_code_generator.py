from functions.advanced_punch_generator import CommandLinesGenerator


def generate_command_lines(params_dict):
    """
    Генерация G-кода для пробития треугольного паттерна радиально-спиральным методом
    со случайными смещениями игл для равномерного покрытия.

    Args:
        params_dict (dict): Словарь параметров пробития

    Returns:
        list: Список строк G-кода с переносами строк
    """
    generator = CommandLinesGenerator(params_dict)
    return generator.generate_radial_spiral_pattern()