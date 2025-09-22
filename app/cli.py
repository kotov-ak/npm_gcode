
from functions.prod_functions import *

from functions.time_calc import *

file_path = '../gcode/g_code_random.txt'


punch_params_dict = dict(
    tube_len=500,
    i_diam=147, # 60+
    o_diam=215, # 300-
    fabric_thickness=0.55, # 0.6
    punch_step_r=3, # 1
    needle_step=8, # 8
    volumetric_density=25,
    punch_head_len=264, # 264
    punch_depth=14, # 12+
    punch_offset=10,
    shoe_depth=5,
    idling_speed=6000, # 3000-5000
    move_speed=750, # 1500
    rotate_speed=1000, # 1000
)

if __name__ == '__main__':
    """
    Записать в файл и вывод информации о программе 
    """
    try:
        print("Generation begins. Please wait...")
        write_in_file_by_lines(triangle_punch_radial_spiral_needle_full_random_upd(punch_params_dict), file_path)
        print("Generation finished!")
    except:
        raise SyntaxError
