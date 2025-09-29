import math as m
from constants.const import GenerationConfig


class GeometryCalculator:
    """Класс для геометрических расчетов пробития"""

    def __init__(self, params_dict):
        """
        Инициализация калькулятора геометрии

        Args:
            params_dict (dict): Словарь параметров пробития
        """
        self.params = params_dict
        self.config = GenerationConfig()
        self.diam_coef = self.config.VOLUMETRIC_DENSITY_MAP[params_dict['volumetric_density']]

    def calculate_rotation_parameters(self):
        """
        Расчет параметров намотки и оборотов

        Returns:
            tuple: (основные_обороты, общие_обороты, расчетный_внешний_диаметр)
        """
        diam_diff = self.params['o_diam'] - self.params['i_diam']
        ideal_rotation_num = diam_diff / (self.params['fabric_thickness'] * 2)

        rotation_delta = m.floor(ideal_rotation_num) % self.diam_coef
        if rotation_delta:
            main_rotation_num = m.floor(ideal_rotation_num) + self.diam_coef - rotation_delta
        else:
            main_rotation_num = m.floor(ideal_rotation_num)

        calculated_o_diam = self.params['i_diam'] + main_rotation_num * self.params['fabric_thickness'] * 2
        total_rotation_num = main_rotation_num + self.config.EXTRA_ROTATIONS

        return main_rotation_num, total_rotation_num, calculated_o_diam

    def calculate_layer_parameters(self, layer_idx):
        """
        Расчет параметров для конкретного слоя

        Args:
            layer_idx (int): Индекс слоя (0-based)

        Returns:
            tuple: (диаметр_текущего_слоя, длина_окружности, количество_шагов, размер_шага)
        """
        current_diameter = self.params['i_diam'] + 2 * self.params['fabric_thickness'] * layer_idx
        circle_len = m.pi * current_diameter

        ideal_steps = circle_len / self.params['punch_step_r']
        steps_num_less = max(2, 2 * m.floor(ideal_steps / 2))
        steps_num_more = max(2, 2 * m.ceil(ideal_steps / 2))

        steps_num_final = min((steps_num_less, steps_num_more),
                              key=lambda n: (abs(circle_len / n - self.params['punch_step_r']), -n))
        step_size_final = round(circle_len / steps_num_final, 3)

        return current_diameter, circle_len, steps_num_final, step_size_final

    def calculate_total_punches(self, total_rotation_num):
        """
        Предварительный расчет общего количества пробитий

        Args:
            total_rotation_num (int): Общее количество оборотов

        Returns:
            tuple: (общее_количество_пробитий, общая_длина_ткани)
        """
        total_cranks = 0
        total_fabric_len = 0

        for i in range(total_rotation_num):
            current_diameter, circle_len, steps_num_final, _ = self.calculate_layer_parameters(i)
            total_cranks += steps_num_final
            total_fabric_len += circle_len

        zones_per_crank = m.ceil(self.params['tube_len'] / self.params['punch_head_len'])
        punches_in_zone = round(self.params['needle_step'] / self.diam_coef)
        total_punches = punches_in_zone * zones_per_crank * total_cranks

        return total_punches, total_fabric_len, zones_per_crank, punches_in_zone