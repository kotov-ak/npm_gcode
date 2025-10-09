from typing import List, Iterator
import math
import numpy as np

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

    def nearest_multiple(self, X: float, divisor: int) -> int:
        """
        Возвращает ближайшее число кратное divisor, которое >= X
        """
        return math.ceil(X / divisor) * divisor
        
    def calclulate_number_of_revolutions(self):
        diam_diff = self.params['o_diam'] - self.params['i_diam']
        ideal_rotation_num = diam_diff / (self.params['fabric_thickness'] * 2)
        return self.nearest_multiple(ideal_rotation_num, self.config.VOLUMETRIC_DENSITY_MAP[self.params['volumetric_density']])
    
    def generate_random_offsets(self, revolutions):
        total_cranks = 0
        for revolution in range(revolutions):
            angle_step_count = self.get_angle_steps_count(revolution)
            total_cranks += angle_step_count
        x_step_count = math.ceil(self.params['tube_len'] / self.params['punch_head_len'])
        volumetric_density = self.config.VOLUMETRIC_DENSITY_MAP[self.params['volumetric_density']]
        x_substep_count = round(self.params['needle_step'] / volumetric_density)
        total_punches = x_substep_count * x_step_count * total_cranks
        self.random_offsets = self._generate_random_offsets(total_punches)

    def generate_punch_pattern_commands(self) -> List[MotionCommand]:
        revolutions = self.calclulate_number_of_revolutions()
        self.generate_random_offsets(revolutions + self.config.EXTRA_ROTATIONS)

        commands = self.generate_commands(revolutions)

        commands.append(PunchCommands.waiting())

        support_offset = self.params['fabric_thickness'] * revolutions
        commands_for_virtual_stitching = self.generate_commands(self.config.EXTRA_ROTATIONS, support_offset)
        commands.extend(commands_for_virtual_stitching)

        return commands

    def _generate_random_offsets(self, total_punches: int) -> np.ndarray:
        """Генерация случайных смещений"""
        seed = self.config.RANDOM_SEED
        rng = np.random.default_rng(seed)
        a = 2 * self.config.CENTER_X - self.params['random_border']
        b = self.params['random_border']
        return rng.uniform(a, b, size=total_punches)

    
    def get_circle_len(self, revolution):
        return math.pi * (self.params['i_diam'] + 2 * self.params['fabric_thickness'] * revolution)

    def get_angle_steps_count(self, revolution):
        circle_len = self.get_circle_len(revolution)
        # «Идеальное» дробное число шагов
        ideal_steps = circle_len / self.params['punch_step_r']
        # ближайшее чётное «большее» и «меньшее» (минимальный шаг 2)
        steps_num_less = max(2, 2 * math.floor(ideal_steps / 2))
        steps_num_more = max(2, 2 * math.ceil(ideal_steps / 2))
        # Выбор лучшего: варианта: первично — минимальное отклонение, при равенстве — большее число шагов
        steps_num_final = min((steps_num_less, steps_num_more),
                            key=lambda n: (abs(circle_len / n - self.params['punch_step_r']), -n))
        return steps_num_final

    def generate_commands(self, revolutions, support_offset = None):
        volumetric_density = self.config.VOLUMETRIC_DENSITY_MAP[self.params['volumetric_density']]
        support_depth = self.params['support_depth']

        x_step_count = math.ceil(self.params['tube_len'] / self.params['punch_head_len'])
        x_step_size = self.params['punch_head_len']
        x_step_offset_1 = 0
        x_step_offset_2 = (x_step_count - 1) * x_step_size
    
        x_substep_count = round(self.params['needle_step'] / volumetric_density)
        x_substep_size = round(self.params['needle_step'] / volumetric_density / x_substep_count ) # params['punch_step_r']
        x_substep_offset_1 = 0
        x_substep_offset_2 = (x_substep_count - 1) * x_substep_size
  
        section_count = volumetric_density # количество оборотов для заполнения полного паттерна вдоль Х (int)
        section_size = self.params['needle_step'] / section_count

        commands = []
        random_offset_it = iter(self.random_offsets)
        for revolution in range(revolutions):
            angle_step_count = self.get_angle_steps_count(revolution)
            angle_step_size = 360 / angle_step_count
            for angle_step in range(angle_step_count):
                angle_deg = round(360 * revolution + angle_step_size * angle_step, 3)
                direction = not bool( ( revolution * angle_step_count + angle_step ) % 2 ) # самый первый удар имеет направление true

                commands.append(PunchCommands.rotate(angle_deg, self.params['rotate_speed']))
                for x_step in range(x_step_count):
                    for x_substep in range(x_substep_count):
                        random_offset = next(random_offset_it)

                        x_snake_offset = ( angle_step % 2 ) * x_substep_size / 2

                        # смещение для слоя (каждый полный оборот)
                        x_section_offset = ( revolution % section_count) * section_size

                        # поддержка обратного движения (для змейкообразного паттерна)
                        start_x_step_offset = x_step_offset_1 if direction else x_step_offset_2
                        x_step_offset = abs(x_step_size * x_step - start_x_step_offset) 

                        # поддержка обратного движения (для змейкообразного паттерна)
                        start_x_substep_offset = x_substep_offset_1 if direction else x_substep_offset_2
                        x_substep_offset = abs(x_substep_size * x_substep - start_x_substep_offset)

                        support_offset = support_offset if support_offset is not None else self.params['fabric_thickness'] * revolution

                        # random_offset = 0
                        x = round(random_offset +
                                  x_snake_offset +
                                  x_section_offset +
                                  x_substep_offset +
                                  x_step_offset, 3)
                        y = round(0 - self.params['fabric_thickness'] * revolution, 3)
                        z = round(0 - support_offset, 3)

                        y_punch = y + self.params['punch_depth'] + self.params['punch_offset']
                        z_punch = z + support_depth

                        commands.append(PunchCommands.approach(x, y, z, self.params['idling_speed']))
                        commands.append(PunchCommands.punch(x, y_punch, z_punch, self.params['move_speed']))
                        commands.append(PunchCommands.retract(x, y, z, self.params['move_speed']))            

        return commands

    def get_generation_statistics(self) -> dict:
        """
        Получить статистику для текущих параметров

        Returns:
            dict: Словарь со статистикой генерации
        """

        main_rotation_num, total_rotation_num, calculated_o_diam = self.geometry.calculate_rotation_parameters()
        total_punches, total_fabric_len, zones_per_crank, punches_in_zone = self.geometry.calculate_total_punches(total_rotation_num)

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
