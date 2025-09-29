from constants.const import ValidationLimits


class ParameterValidator:
    """Класс для валидации параметров пробития"""

    def __init__(self):
        self.limits = ValidationLimits()

    def validate_all_parameters(self, params_dict):
        """
        Проверка всех параметров на корректность

        Args:
            params_dict (dict): Словарь с параметрами для проверки

        Returns:
            tuple: (bool, str, str) - (успех, имя_параметра, сообщение_об_ошибке)
        """
        # Проверка на положительные и ненулевые значения
        result = self._check_positive_values(params_dict)
        if not result[0]:
            return result

        # Проверка габаритных ограничений
        result = self._check_dimensional_limits(params_dict)
        if not result[0]:
            return result

        # Проверка дискретных значений
        result = self._check_discrete_values(params_dict)
        if not result[0]:
            return result

        return True, None, None

    def _check_positive_values(self, params_dict):
        """Проверка на положительные значения"""
        for param_name, param_value in params_dict.items():
            if param_value <= 0:
                return False, param_name, f"Значение должно быть положительным числом (получено: {param_value})"
            if param_value == '':
                return False, param_name, "Значение не может быть пустым"
        return True, None, None

    def _check_dimensional_limits(self, params_dict):
        """Проверка габаритных ограничений"""
        checks = [
            (params_dict['tube_len'] >= self.limits.MAX_TUBE_LENGTH + 0.001, 'tube_len',
             f"Длина трубы должна быть < {self.limits.MAX_TUBE_LENGTH} мм (получено: {params_dict['tube_len']})"),

            (params_dict['i_diam'] <= self.limits.MIN_INNER_DIAMETER - 0.001, 'i_diam',
             f"Внутренний диаметр должен быть > {self.limits.MIN_INNER_DIAMETER} мм (получено: {params_dict['i_diam']})"),

            (params_dict['i_diam'] >= self.limits.MAX_INNER_DIAMETER + 0.001, 'i_diam',
             f"Внутренний диаметр должен быть < {self.limits.MAX_INNER_DIAMETER} мм (получено: {params_dict['i_diam']})"),

            (params_dict['o_diam'] >= self.limits.MAX_OUTER_DIAMETER + 0.001, 'o_diam',
             f"Внешний диаметр должен быть < {self.limits.MAX_OUTER_DIAMETER} мм (получено: {params_dict['o_diam']})"),

            (params_dict['o_diam'] <= self.limits.MIN_OUTER_DIAMETER - 0.001, 'o_diam',
             f"Внешний диаметр должен быть > {self.limits.MIN_OUTER_DIAMETER} мм (получено: {params_dict['o_diam']})"),

            (params_dict['i_diam'] > params_dict['o_diam'], 'i_diam',
             f"Внутренний диаметр ({params_dict['i_diam']}) не может быть больше внешнего ({params_dict['o_diam']})"),

            (params_dict['punch_step_r'] > params_dict['i_diam'] * 3.14, 'punch_step_r',
             f"Окружной шаг ({params_dict['punch_step_r']}) слишком большой для внутреннего диаметра {params_dict['i_diam']} мм"),

            (params_dict['punch_depth'] >= self.limits.MAX_PUNCH_DEPTH + 0.001, 'punch_depth',
             f"Глубина пробития должна быть < {self.limits.MAX_PUNCH_DEPTH} мм (получено: {params_dict['punch_depth']})"),

            (params_dict['idling_speed'] >= self.limits.MAX_IDLING_SPEED + 0.001, 'idling_speed',
             f"Скорость холостого хода должна быть < {self.limits.MAX_IDLING_SPEED} мм/мин (получено: {params_dict['idling_speed']})"),

            (params_dict['move_speed'] >= self.limits.MAX_MOVE_SPEED + 0.001, 'move_speed',
             f"Скорость пробития должна быть < {self.limits.MAX_MOVE_SPEED} мм/мин (получено: {params_dict['move_speed']})"),

            (params_dict['rotate_speed'] >= self.limits.MAX_ROTATE_SPEED + 0.001, 'rotate_speed',
             f"Скорость поворота должна быть < {self.limits.MAX_ROTATE_SPEED} мм/мин (получено: {params_dict['rotate_speed']})")
        ]

        for check_failed, param_name, error_message in checks:
            if check_failed:
                return False, param_name, f"{error_message}."

        return True, None, None

    def _check_discrete_values(self, params_dict):
        """Проверка дискретных значений"""
        checks = [
            (params_dict['volumetric_density'] not in self.limits.ALLOWED_VOLUMETRIC_DENSITIES, 'volumetric_density',
             f"Объемная плотность должна быть {', '.join(map(str, self.limits.ALLOWED_VOLUMETRIC_DENSITIES))} (получено: {params_dict['volumetric_density']})"),

            (params_dict['punch_step_r'] not in self.limits.ALLOWED_PUNCH_STEPS, 'punch_step_r',
             f"Шаг пробития должен быть {', '.join(map(str, self.limits.ALLOWED_PUNCH_STEPS))} мм (получено: {params_dict['punch_step_r']})"),

            (params_dict['needle_step'] != self.limits.REQUIRED_NEEDLE_STEP, 'needle_step',
             f"Шаг игл должен быть равен {self.limits.REQUIRED_NEEDLE_STEP} мм (получено: {params_dict['needle_step']})")
        ]

        for check_failed, param_name, error_message in checks:
            if check_failed:
                return False, param_name, f"{error_message}."

        return True, None, None