#!/usr/bin/env python3
"""
Базовые тесты функциональности генератора
"""

import sys
import os
import unittest

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.advanced_punch_generator import CommandLinesGenerator
from functions.time_calc import time_prediction_motioncommand
from functions.prod_functions import calculate_execution_time


class TestBasicFunctionality(unittest.TestCase):
    """Базовые тесты функциональности"""

    def setUp(self):
        """Настройка тестов"""
        self.minimal_params = {
            'tube_len': 264,
            'i_diam': 10,
            'o_diam': 10,
            'fabric_thickness': 1.0,
            'punch_step_r': 1,
            'needle_step': 8,
            'volumetric_density': 25,
            'punch_head_len': 264,
            'punch_depth': 14,
            'punch_offset': 10,
            'support_depth': 5,
            'idling_speed': 6000,
            'move_speed': 1200,
            'rotate_speed': 2000,
        }

    def test_generator_creation(self):
        """Тест создания генератора"""
        generator = CommandLinesGenerator(self.minimal_params)
        self.assertIsNotNone(generator)
        self.assertEqual(generator.params, self.minimal_params)

    def test_command_generation(self):
        """Тест генерации команд"""
        generator = CommandLinesGenerator(self.minimal_params)
        commands = generator.generate_commands_only()

        self.assertIsInstance(commands, list)
        self.assertGreater(len(commands), 10)

        # Проверяем, что есть команды разных типов
        command_types = [cmd.command_type.value for cmd in commands]
        self.assertIn("G01", command_types)

    def test_time_calculation(self):
        """Тест расчета времени выполнения"""
        time_data = calculate_execution_time(self.minimal_params)

        self.assertIsInstance(time_data, list)
        self.assertEqual(len(time_data), 3)  # Part1, Part2, Total

        # Проверяем формат возвращаемых данных
        for part in time_data:
            self.assertEqual(len(part), 2)  # [time_string, time_seconds]
            self.assertIsInstance(part[0], str)  # Время в виде строки
            self.assertIsInstance(part[1], (int, float))  # Время в секундах

    def test_generation_statistics(self):
        """Тест получения статистики генерации"""
        generator = CommandLinesGenerator(self.minimal_params)
        stats = generator.get_statistics()

        self.assertIsInstance(stats, dict)

        # Проверяем наличие ключевых статистических данных
        expected_keys = ['main_rotation_num', 'total_rotation_num', 'total_punches']
        for key in expected_keys:
            self.assertIn(key, stats)
            self.assertIsInstance(stats[key], (int, float))

    def test_file_generation(self):
        """Тест генерации файла"""
        generator = CommandLinesGenerator(self.minimal_params)
        lines = generator.generate_radial_spiral_pattern()

        with open("last_test.txt", "w") as f:
            f.writelines(lines)

        self.assertIsInstance(lines, list)
        self.assertGreater(len(lines), 50)

        # Проверяем, что есть заголовок и команды
        file_content = ''.join(lines)
        self.assertIn('G-code has been generated', file_content)
        self.assertIn('G01', file_content)


if __name__ == '__main__':
    unittest.main(verbosity=2)