import math as m


def stepsize_calculation(diameter, target_step, num_of_needle_rows, dist_btw_needles):
    """
    Разбивает окружность на части, кратные base
    """
    # Длина окружности
    circ_len = m.pi * diameter
    # Величина смещения игольницы по окружности
    radial_head_offset = num_of_needle_rows * dist_btw_needles

    # Идеальное количество шагов
    ideal_steps = circ_len / target_step

    # Два ближайших варианта, кратных radial_head_offset
    low_steps = max(radial_head_offset, m.floor(ideal_steps / radial_head_offset) * radial_head_offset)
    high_steps = m.ceil(ideal_steps / radial_head_offset) * radial_head_offset

    # Считаем шаги для каждого варианта
    step_low = circ_len / low_steps
    step_high = circ_len / high_steps

    # Выбираем вариант с шагом ближе к целевому
    if abs(step_low - target_step) <= abs(step_high - target_step):
        final_steps = low_steps
        final_step_size = step_low
    else:
        final_steps = high_steps
        final_step_size = step_high

    return {
        'circ_len': circ_len,
        'final_step_size': final_step_size,
        'final_steps_num': final_steps,
        'radial_head_offset': radial_head_offset,
        'radial_head_offset_zones': final_steps/radial_head_offset,
        'stepsize_diff_pcent': abs(final_step_size-target_step)/target_step*100,
    }


def print_result(result):
    """
    Красиво выводит информацию о разбиении окружности
    """
    print(f"Длина окружности: {round(result['circ_len'], 3)} мм")
    print(f"Вычисленный шаг: {round(result['final_step_size'], 3)} мм")
    print(f"Общее число шагов: {round(result['final_steps_num'], 3)}")

    print("-" * 50)


# Пример использования
if __name__ == "__main__":
    diameter = 100
    step = 1
    needle_rows = 3
    dist_btw_needles = 8

    result = stepsize_calculation(diameter, step, needle_rows, dist_btw_needles)

    print(result)
    print_result(result)
