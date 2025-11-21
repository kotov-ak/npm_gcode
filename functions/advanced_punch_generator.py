from typing import List
# Добавляем родительский каталог в путь для импорта модулей
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from functions.tube_command_generator import TubeCommandGenerator
from functions.gcode_file_formatter import GCodeFileFormatter
from functions.motion_commands import MotionCommand


class CommandLinesGenerator:
    """
    Продвинутый генератор паттернов пробития с использованием структурированных команд.
    Объединяет генерацию команд и их форматирование в текстовый файл.
    """

    def __init__(self, params_dict: dict):
        """
        Инициализация продвинутого генератора

        Args:
            params_dict (dict): Словарь параметров пробития
        """
        self.params = params_dict
        self.command_generator = TubeCommandGenerator(params_dict)
        self.file_formatter = GCodeFileFormatter(params_dict)

    def generate_radial_spiral_pattern(self) -> List[str]:
        """
        Генерация радиально-спирального паттерна пробития в виде текстовых строк

        Returns:
            List[str]: Список строк G-кода с переносами строк
        """

        commands = self.command_generator.generate_punch_pattern_commands()
        generation_stats = self.command_generator.get_generation_statistics()

        formatted_lines = self.file_formatter.format_to_lines(
            commands,
            generation_stats,
            "generate_command_lines"
        )

        return formatted_lines

    def generate_commands_only(self) -> List[MotionCommand]:
        """
        Генерация только структурированных команд без форматирования

        Returns:
            List[MotionCommand]: Список структурированных команд
        """
        return self.command_generator.generate_punch_pattern_commands()

    def get_statistics(self) -> dict:
        """
        Получить статистику генерации

        Returns:
            dict: Словарь со статистикой
        """
        return self.command_generator.get_generation_statistics()

    def get_command_statistics(self, commands: List[MotionCommand] = None) -> dict:
        """
        Получить статистику команд

        Args:
            commands (List[MotionCommand], optional): Команды для анализа.
                                                     Если None, генерирует новые.

        Returns:
            dict: Статистика команд
        """
        if commands is None:
            commands = self.generate_commands_only()

        return self.file_formatter.count_command_statistics(commands)

    def print_generation_info(self, verbose: bool = False):
        """
        Вывод информации о генерации

        Args:
            verbose (bool): Подробный вывод
        """
        stats = self.get_statistics()

        print("=== ИНФОРМАЦИЯ О ГЕНЕРАЦИИ G-КОДА ===")
        print(f"Основные обороты: {stats['main_rotation_num']}")
        print(f"Всего оборотов: {stats['total_rotation_num']}")
        print(f"Рассчитанный внешний диаметр: {stats['calculated_o_diam']:.2f} мм")
        print(f"Общая длина ткани: {round(stats['total_fabric_len'])} мм")
        print(f"Всего пробитий: {stats['total_punches']}")
        print(f"Seed для случайных смещений: {stats['random_seed']}")

        if verbose:
            commands = self.generate_commands_only()
            cmd_stats = self.get_command_statistics(commands)
            print("\n=== СТАТИСТИКА КОМАНД ===")
            for key, value in cmd_stats.items():
                print(f"{key}: {value}")


# Простая генерация для тестирования
if __name__ == '__main__':
    minimal_params = {
        'tube_len': 264,
        'i_diam': 10,
        'o_diam': 11,
        'fabric_thickness': 1.0,
        'punch_step_r': 1,
        'needle_step_X': 8,
        'needle_step_Y': 8,
        'volumetric_density': 25,
        'head_len': 264,
        'punch_depth': 14,
        'punch_offset': 10,
        'zero_offset_Y': 100,
        'zero_offset_Z': 100,
        'support_depth': 5,
        'idling_speed': 6000,
        'move_speed': 1200,
        'rotate_speed': 2000,
        'random_border': 0.25,
        'num_of_needle_rows': 1
    }
            
    generator = CommandLinesGenerator(minimal_params)
    lines = generator.generate_radial_spiral_pattern()

    with open("last_test.txt", "w") as f:
        f.writelines(lines)