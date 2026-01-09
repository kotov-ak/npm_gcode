# Добавляем родительский каталог в путь для импорта модулей
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List
import math
import numpy as np
from itertools import zip_longest

from constants.const import GenerationConfig
from functions.geometry_calculator import GeometryCalculator
from functions.motion_commands import MotionCommand, PunchCommands, CommandType


class TubeCommandGenerator:
    """
    Генератор команд для пробития трубы.
    Создает структурированные команды движения без их текстового форматирования.
    """

    def __init__(self, params_dict: dict):
        """
        Инициализация генератора команд

        Args:
            params_dict (dict): Словарь параметров пробития
        """
        self.params = params_dict
        self.config = GenerationConfig()
        self.geometry = GeometryCalculator(params_dict)
        self.completed_revolutions = 0  # Смещение оборотов для продолжения генерации

    def nearest_multiple(self, X: float, divisor: int) -> int:
        """
        Возвращает ближайшее число кратное divisor, которое >= X
        """
        return math.ceil(X / divisor) * divisor

    def reorder_range(self,x):
        """
        Переставляет числа от 0 до x-1, чередуя первую и вторую половину.
        Например: [0,1,2,3,4] -> [0,3,1,4,2]
        """
        lst = list(range(x))
        mid = (x + 1) // 2
        return [i for pair in zip_longest(lst[:mid], lst[mid:])
                for i in pair if i is not None]
            
    def calclulate_number_of_revolutions(self):
        diam_diff = self.params['o_diam'] - self.params['i_diam']
        ideal_rotation_num = diam_diff / (self.params['fabric_thickness'] * 2)

        number_of_layers_to_fill_the_entire_pattern = round(self.params['x_substep_count'] / self.params['x_substep_count_in_one_revolution']) # а если 7 на 2?
        return self.nearest_multiple(ideal_rotation_num, number_of_layers_to_fill_the_entire_pattern)
    
    def generate_random_offsets(self, revolutions):
        total_cranks = 0
        for revolution in range(revolutions):
            angle_step_count = self.get_angle_steps_count(revolution)
            total_cranks += angle_step_count
        x_step_count = math.ceil(self.params['tube_len'] / self.params['head_len'])
        x_substep_count_in_one_revolution = self.params['x_substep_count_in_one_revolution']
        total_punches = x_substep_count_in_one_revolution * x_step_count * total_cranks
        self.random_offsets = self._generate_random_offsets(total_punches)
        self.punch_counter = 0

    def generate_punch_pattern_commands(self) -> List[MotionCommand]:
        revolutions = self.calclulate_number_of_revolutions()
        self.generate_random_offsets(revolutions + self.config.EXTRA_ROTATIONS)

        commands = self.generate_commands(revolutions)

        if (len(commands) > 0):
            commands.append(PunchCommands.waiting())

        fix_z_offset = self.params['fabric_thickness'] * revolutions
        commands_for_virtual_stitching = self.generate_commands(self.config.EXTRA_ROTATIONS, fix_z_offset=fix_z_offset)
        commands.extend(commands_for_virtual_stitching)

        return commands

    def _generate_random_offsets(self, total_punches) -> np.ndarray:
        """Генерация случайных смещений"""
        seed = self.config.RANDOM_SEED
        rng = np.random.default_rng(seed)
        a = 2 * self.config.CENTER_X - self.params['random_border']
        b = self.params['random_border']
        return rng.uniform(a, b, size=round(total_punches))
    
    def get_circle_len(self, revolution):
        return math.pi * (self.params['i_diam'] + 2 * self.params['fabric_thickness'] * revolution)

    def get_angle_steps_count(self, revolution):
        """
        Определяет оптимальное количество шагов для определенного диаметра
        Расчет ведётся исходя из целевого шага self.params['punch_step_r']
        Количества рядов игл из self.params['num_of_needle_rows']
        Расстояния между рядами игл из self.params["needles_dist_y"]

        """
        # Величина смещения игольницы по окружности
        if self.params['num_of_needle_rows'] == 1:
            radial_head_offset = round(2.0)
        else:
            radial_head_offset = round(self.params['num_of_needle_rows'] * self.params['needle_step_Y'])

        # Идеальное количество шагов
        circle_len = self.get_circle_len(revolution)
        ideal_steps = circle_len / self.params['punch_step_r']

        # Два ближайших варианта, кратных radial_head_offset
        low_steps = max(radial_head_offset, math.floor(ideal_steps / radial_head_offset) * radial_head_offset)
        high_steps = math.ceil(ideal_steps / radial_head_offset) * radial_head_offset
        step_low = circle_len / low_steps
        step_high = circle_len / high_steps

        # Выбираем вариант с шагом ближе к целевомуs
        if abs(step_low - self.params['punch_step_r']) <= abs(step_high - self.params['punch_step_r']):
            final_steps = low_steps
        else:
            final_steps = high_steps

        return final_steps

    def generate_commands(self, revolutions, fix_z_offset=None):
        support_depth = self.params['support_depth']
        num_of_needle_rows = self.params['num_of_needle_rows']

        x_step_count = math.ceil(self.params['tube_len'] / self.params['head_len'])
        x_step_size = self.params['head_len']

        x_substep_count = self.params['x_substep_count']
        x_substep_size = self.params['needle_step_X'] / x_substep_count

        section_count = self.params['x_substep_count'] // self.params['x_substep_count_in_one_revolution'] # а если 7 на 2?
        section_size = self.params['x_substep_count_in_one_revolution'] 

        commands = []

        substeps_order = list(range(self.params['x_substep_count']))
        # substeps_order = self.reorder_range(self.params['x_substep_count_in_one_revolution']) #  новая версия, раскомментировать вместе с апдейтом тестов

        start = self.completed_revolutions
        finish = self.completed_revolutions + revolutions
        for revolution in range(start, finish):
            angle_step_count = self.get_angle_steps_count(revolution)
            angle_step_size = 360 / angle_step_count

            section = revolution % section_count
            start_substep_idx = section * section_size
            finish_substep_idx = start_substep_idx + section_size
            substep_direct_order = substeps_order[start_substep_idx:finish_substep_idx]

            for angle_step in range(angle_step_count):
                angle_deg = 360 * revolution + angle_step_size * angle_step

                circumferential_head_step = num_of_needle_rows * self.params['needle_step_Y']
                # пробиваем зоны между иглами (в радиальном направлении)
                # если заполнили то делаем проворот на всю длину игольницы
                if self.params['needle_step_Y'] <= (angle_step % circumferential_head_step) <= (circumferential_head_step - 1):
                    commands.append(PunchCommands.rotate(angle_deg, self.params['rotate_speed']))
                    continue

                is_direct_order = (revolution * angle_step_count + angle_step) % 2 == 0 # самый первый удар имеет направление true

                commands.append(PunchCommands.rotate(angle_deg, self.params['rotate_speed']))

                step_order = range(x_step_count) if is_direct_order else reversed(range(x_step_count))      
                substep_order = substep_direct_order if is_direct_order else substep_direct_order[::-1]

                for x_step in step_order:
                    for x_substep in substep_order:
                        random_offset = self.random_offsets[self.punch_counter]
                        self.punch_counter += 1
                        x_snake_offset = (angle_step % 2) * x_substep_size / 2

                        x_step_offset = x_step_size * x_step
                        x_substep_offset = x_substep_size * x_substep

                        y_offset = self.params['fabric_thickness'] * revolution
                        z_offset = fix_z_offset if fix_z_offset is not None else self.params['fabric_thickness'] * revolution

                        x = random_offset + x_snake_offset + x_substep_offset + x_step_offset
                        y = self.params['zero_offset_Y'] - self.params['punch_offset'] - y_offset
                        z = self.params['zero_offset_Z'] - z_offset
                        
                        y_punch = y + self.params['punch_depth'] + self.params['punch_offset']
                        z_punch = z + support_depth

                        commands.append(PunchCommands.approach(x, y, z, self.params['idling_speed']))
                        commands.append(PunchCommands.punch(x, y_punch, z_punch, self.params['move_speed']))
                        commands.append(PunchCommands.retract(x, y, z, self.params['move_speed']))

        self.completed_revolutions += revolutions # Сохраняем для следующих вызовов функции
        return commands

    def get_generation_statistics(self) -> dict:
        """
        Получить статистику для текущих параметров

        Returns:
            dict: Словарь со статистикой генерации
        """

        main_rotation_num, total_rotation_num, calculated_o_diam = self.geometry.calculate_rotation_parameters()
        total_punches, total_fabric_len, zones_per_crank, punches_in_zone = self.geometry.calculate_total_punches(main_rotation_num, total_rotation_num)

        return {
            'main_rotation_num': main_rotation_num,
            'total_rotation_num': total_rotation_num,
            'calculated_o_diam': calculated_o_diam,
            'total_punches': total_punches,
            'total_fabric_len': total_fabric_len,
            'zones_per_crank': zones_per_crank,
            'punches_in_zone': punches_in_zone,
            'random_seed': self.config.RANDOM_SEED
        }
    
# Простая генерация для тестирования
if __name__ == '__main__':
    minimal_params = {
        'tube_len': 528,
        'i_diam': 60,
        'o_diam': 70,
        'fabric_thickness': 1.0,
        'punch_step_r': 1, # изменяем этот параметр для получения заданной поверхностной плотности пробивки
        'needle_step_X': 8,
        'needle_step_Y': 8,
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
        'num_of_needle_rows': 1,
        'x_substep_count': 8,
        'x_substep_count_in_one_revolution': 2,
    }
            
    generator = TubeCommandGenerator(minimal_params)
    commands = generator.generate_punch_pattern_commands()