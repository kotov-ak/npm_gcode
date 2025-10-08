

# словарь с режимами пробития
punch_mode_dict = {
    'Стандартный': 1
}

# словарь с методом получения данных
data_mode_dict = {
    'Ручной ввод': 1
}

# Словарь соответствия режимов и функций-обработчиков
# Ключ: (режим_пробития, режим_данных)
# Значение: имя метода в MainWindow
MODE_HANDLERS = {
    ('Стандартный', 'Ручной ввод'): 'punch_mode_11',
}


class GenerationConfig:
    """Конфигурация для генерации G-кода"""

    # Отладка
    DEBUG_OUTPUT = False
    DEBUG_TO_FILE = False

    # Алгоритм
    EXTRA_ROTATIONS = 20
    CENTER_X = 0.0
    RANDOM_SEED = 5
    RANDOM_AMPLITUDE = 0.5

    # Соответствие объемной плотности к коэффициенту диаметров
    VOLUMETRIC_DENSITY_MAP = {15: 8, 25: 4, 45: 2}


class ValidationLimits:
    """Ограничения для валидации параметров"""

    # Габаритные ограничения
    MAX_TUBE_LENGTH = 1200.0
    MIN_INNER_DIAMETER = 10.0
    MAX_INNER_DIAMETER = 300.0
    MIN_OUTER_DIAMETER = 10.0
    MAX_OUTER_DIAMETER = 320.0
    MAX_PUNCH_DEPTH = 15.0
    MAX_IDLING_SPEED = 10000.0
    MAX_MOVE_SPEED = 2500.0
    MAX_ROTATE_SPEED = 2000.0

    # Дискретные значения
    ALLOWED_VOLUMETRIC_DENSITIES = (15, 25, 45)
    ALLOWED_PUNCH_STEPS = (1, 2, 4)
    REQUIRED_NEEDLE_STEP = 8


advanced_dict = dict(
    tube_len=528, # 0-264=1, 265-528=2, 529-729=3,
    i_diam=102, # 60+
    o_diam=132, # 300-
    fabric_thickness=0.6, # 0.6
    punch_step_r=1, # 1
    needle_step=8, # 8
    volumetric_density=25,
    punch_head_len=264, # 264
    punch_depth=14, # 12+
    punch_offset=10,
    support_depth=5,
    idling_speed=5000, # 3000-5000
    move_speed=1500, # 1500
    rotate_speed=1000, # 1000
    random_border=0.5 # 0-0.5
)


base_description = '''
Программа позволяет сгенерировать программный код (G-код) для 
иглопробивного станка. Генерация происходит на основе данных о
требуемом изделии, а также параметрах пробития. Задание
параметров происходит вручную через интерфейс.

Описание алгоритма (правил) работы с программой:

1) Выбрать режим пробития в соответствующей графе (Стандартный)
2) Выбрать источник данных в соответствующей графе (Ручной ввод)
3) Заполнить все поля параметров требуемыми значениями
5) Указать название файла для сохранения G-кода (без расширения, только имя)
6) Выбрать папку для сохранения G-кода
6) Проверить информация о параметрах, пусти сохранения и нажать кнопку генерации G-кода
'''

version_description = '''
version 1.1
'''