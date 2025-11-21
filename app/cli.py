
import sys
import os

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.prod_functions import write_in_file_by_lines
from functions.prod_functions import generate_command_lines

file_path = '../gcode/g_code_random.txt'


punch_params_dict = dict(
    tube_len=300,
    i_diam=80, # 60+
    o_diam=100, # 300-
    fabric_thickness=0.5, # 0.6
    punch_step_r=1, # 1
    needle_step_X=8, # 8
    needle_step_Y=8, # 8-16
    volumetric_density=25,
    head_len=264, # 264
    punch_depth=15, # 12+
    punch_offset=10,
    zero_offset_Y=100,
    zero_offset_Z=100,
    support_depth=5,
    idling_speed=5000, # 3000-5000
    move_speed=1000, # 1500
    rotate_speed=2000, # 1000
    random_border=0, # 0-0.5
    num_of_needle_rows=1 # количество рядов игл
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
