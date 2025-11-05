from typing import List, Dict, Any
from datetime import datetime

from functions.motion_commands import MotionCommand
from functions.time_calc import time_prediction_motioncommand


class GCodeFileFormatter:
    """
    Класс для форматирования команд в текстовый файл G-кода с заголовками и комментариями
    """

    def __init__(self, params_dict: dict):
        """
        Инициализация форматировщика

        Args:
            params_dict (dict): Словарь параметров пробития
        """
        self.params = params_dict

    def format_to_lines(self, commands: List[MotionCommand],
                       generation_stats: dict,
                       function_name: str = "generate_command_lines") -> List[str]:
        """
        Форматирование команд в список строк для файла

        Args:
            commands (List[MotionCommand]): Список команд
            generation_stats (dict): Статистика генерации
            function_name (str): Имя функции для заголовка

        Returns:
            List[str]: Список строк файла с переносами строк
        """
        lines = []

        # Добавляем информационный заголовок
        header_lines = self._generate_header(generation_stats, function_name, commands)
        lines.extend(header_lines)

        # Добавляем команды
        command_lines = self._format_commands(commands)
        lines.extend(command_lines)

        # Добавляем переносы строк
        return [line + '\n' for line in lines]

    def _generate_header(self, stats: dict, function_name: str, commands: List[MotionCommand]) -> List[str]:
        """Генерация информационного заголовка"""
        comment_symbol = ';'

        # Используем оптимизированную функцию для расчета времени
        time_data = time_prediction_motioncommand(commands)

        info_lines = [
            'G-code has been generated based on ',
            f'"{function_name}" function',
            f'at {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}',
            '-' * 50,
            f'Part 1 => {time_data[0][0]} ({time_data[0][1]})',
            f'Part 2 => {time_data[1][0]} ({time_data[1][1]})',
            f'Total => {time_data[2][0]} ({time_data[2][1]})',
            '-' * 50,
            'Generation parameters:',
            f'Tube length => {self.params["tube_len"]}',
            f'Internal diameter => {self.params["i_diam"]}',
            f'Outer diameter => {self.params["o_diam"]}',
            f'Fabric thickness => {self.params["fabric_thickness"]}',
            f'Punch step => {self.params["punch_step_r"]}',
            f'Needles step X => {self.params["needle_step_X"]}',
            f'Needles step Y => {self.params["needle_step_Y"]}',
            f'Volumetric density => {self.params["volumetric_density"]}',
            f'Punch head len => {self.params["head_len"]}',
            f'Punch depth => {self.params["punch_depth"]}',
            f'Shoe depth => {self.params["support_depth"]}',
            f'Punch offset => {self.params["punch_offset"]}',
            f'Idling speed => {self.params["idling_speed"]}',
            f'Move_speed => {self.params["move_speed"]}',
            f'Rotate_speed => {self.params["rotate_speed"]}',
            '-' * 50,
            'Additional calculated parameters:',
            f'Calculated diameter => {stats["calculated_o_diam"]}',
            f'Main rotation number => {stats["main_rotation_num"]}',
            f'Fabric length => {round(stats["total_fabric_len"])}',
            f'Total punch number => {stats["total_punches"]}',
            f'Seed for random => {stats["random_seed"]}',
            '#' * 50
        ]

        return [comment_symbol + line for line in info_lines]

    def _format_commands(self, commands: List[MotionCommand]) -> List[str]:
        """Форматирование команд в строки G-кода"""
        return [command.to_gcode_string() for command in commands]

    def count_command_statistics(self, commands: List[MotionCommand]) -> Dict[str, int]:
        """
        Подсчет статистики команд

        Args:
            commands (List[MotionCommand]): Список команд

        Returns:
            Dict[str, int]: Статистика команд
        """
        stats = {
            'total_commands': len(commands),
            'linear_moves': 0,
            'rotations': 0,
            'm_codes': 0,
            'pauses': 0,
            'punch_sequences': 0  # Группы из 3 команд: подход-внедрение игл-извлечение игл
        }

        punch_sequence_count = 0

        for i, command in enumerate(commands):
            if command.command_type.value == "G01":
                stats['linear_moves'] += 1

                # Проверяем на поворот (только ось A)
                if (command.a is not None and
                    command.x is None and command.y is None and command.z is None):
                    stats['rotations'] += 1

                # Считаем последовательности пробития
                if (command.comment and
                    any(keyword in command.comment for keyword in ["Подход", "Внедрение игл", "Извлечение игл"])):
                    punch_sequence_count += 1
                    if punch_sequence_count % 3 == 0:
                        stats['punch_sequences'] += 1

            elif command.command_type.value == "M":
                stats['m_codes'] += 1
            elif command.command_type.value == "G04":
                stats['pauses'] += 1

        return stats

    def format_statistics_summary(self, commands: List[MotionCommand]) -> List[str]:
        """
        Форматирование сводки статистики команд

        Args:
            commands (List[MotionCommand]): Список команд

        Returns:
            List[str]: Строки со статистикой
        """
        stats = self.count_command_statistics(commands)

        summary = [
            f"Статистика сгенерированного G-кода:",
            f"  Общее количество команд: {stats['total_commands']}",
            f"  Команды G01 (движение): {stats['linear_moves']}",
            f"  Команды поворота: {stats['rotations']}",
            f"  Последовательности пробития: {stats['punch_sequences']}",
            f"  Команды M (паузы): {stats['m_codes']}",
            f"  Команды G04 (паузы): {stats['pauses']}"
        ]

        return summary