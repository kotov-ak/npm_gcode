
import sys
import os

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.prod_functions import write_in_file_by_lines
from functions.tube_g_code_generator import generate_command_lines

file_path = 'gcode/g_code_random.txt'


punch_params_dict = dict(
    tube_len=264,
    i_diam=50, # 60+
    o_diam=51, # 300-
    fabric_thickness=1.0, # 0.6
    punch_step_r=1, # 1
    needle_step=8, # 8
    volumetric_density=25,
    punch_head_len=264, # 264
    punch_depth=14, # 12+
    punch_offset=10,
    support_depth=5,
    idling_speed=6000, # 3000-5000
    move_speed=1200, # 1500
    rotate_speed=2000, # 1000
)

if __name__ == '__main__':
    """
    Записать в файл и вывод информации о программе 
    """
    try:
        print("Generation begins. Please wait...")
        write_in_file_by_lines(generate_command_lines(punch_params_dict), file_path)
        print("Generation finished!")
    except:
        raise SyntaxError
