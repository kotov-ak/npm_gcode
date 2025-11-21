# Модуль визуализации паттернов пробития

Этот модуль предназначен для создания 3D и 2D визуализации паттернов пробития иглопробивного станка.

## Структура модуля

```
visualization/
├── __init__.py          # Точка входа модуля
├── pattern.py     # 3D визуализация (цилиндр)
├── pattern_2d.py  # 2D визуализация (развёртка)
├── needle_positions.py  # Визуализация позиций игл
├── config.py           # Конфигурационные параметры
├── utils.py            # Утилитарные функции
├── README.md           # Документация модуля
└── README_NEEDLES.md   # Документация визуализации игл
```

## Основные компоненты

### 1. visualization.py (3D визуализация)
Содержит функции для создания 3D визуализации на цилиндре:
- `create_punch_visualization()` - главная функция создания 3D визуализации
- `draw_visualization()` - создание 3D plotly графика с цилиндром

### 2. visualization_2d.py (2D визуализация развёртки)
Содержит функции для создания 2D развёртки цилиндрической поверхности:
- `create_punch_visualization_2d()` - главная функция создания 2D визуализации
- `draw_2d_visualization()` - создание 2D plotly графика развёртки
- Отображает точки в прямоугольном окне needle_step_X × needle_step_Y (8×8 мм по умолчанию)
- Преобразование координат: y_2d = theta * radius

### 3. needle_positions.py (визуализация позиций игл)
Содержит функции для визуализации расположения игл в прямоугольном паттерне:
- `create_needle_visualization()` - главная функция создания визуализации позиций игл
- `calculate_needle_positions()` - расчет координат игл в регулярном паттерне
- Отображает иглы в прямоугольной области с настраиваемыми отступами
- Автоматическая проверка деления head_len на needle_step_X с предупреждениями
- **Полная документация:** [README_NEEDLES.md](README_NEEDLES.md)

### 4. config.py
Конфигурационные параметры:
- `VisualizationConfig` - класс с настройками визуализации паттернов пробития (3D/2D)
- `NeedleVisualizationConfig` - класс с настройками визуализации позиций игл
- Цвета, размеры точек, настройки цилиндра, отступы и макета

### 5. utils.py
Утилитарные функции:
- `lighten_hex()` - осветление HEX цветов
- `validate_output_path()` - валидация путей сохранения
- `create_cylinder_surface()` - создание поверхности цилиндра
- `filter_points_by_turn()` - фильтрация точек для производительности
- `get_visualization_stats()` - статистика визуализации
- `log_visualization_stats()` - вывод статистики в консоль

## Использование

### 3D визуализация (цилиндр)
```python
from visualization import create_punch_visualization

# Параметры пробития
params = {
    'i_diam': 102,
    'o_diam': 132,
    'tube_len': 528,
    'volumetric_density': 25,
    # ... другие параметры
}

# Создание 3D визуализации
create_punch_visualization(params, "output_3d.html")
```

### 2D визуализация (развёртка)
```python
from visualization.visualization_2d import create_punch_visualization_2d

# Параметры пробития (те же самые)
params = {
    'i_diam': 102,
    'needle_step_X': 8,
    'needle_step_Y': 8,
    'volumetric_density': 25,
    # ... другие параметры
}

# Создание 2D визуализации развёртки
create_punch_visualization_2d(params, "output_2d.html")
```

### Визуализация позиций игл
```python
from visualization import create_needle_visualization

# Создание визуализации позиций игл
fig, warning, warning_message = create_needle_visualization(
    needle_step_X=8,
    needle_step_Y=8,
    head_len=264,
    num_of_needle_rows=1,
    output_file="needle_positions.html",
    auto_open=True
)

if warning:
    print(warning_message)
```

### Получение статистики
```python
from visualization.utils import get_visualization_stats

# Получение статистики точек
stats = get_visualization_stats(all_hits)
print(f"Общее количество точек: {stats['total_points']}")
```

## Особенности

### Обработка ошибок
- Подробный вывод ошибок в консоль с префиксом `[ВИЗУАЛИЗАЦИЯ]`
- Валидация входных параметров
- Проверка путей сохранения файлов

### Статистика
- Автоматический вывод статистики точек
- Информация о диапазонах координат
- Распределение точек по оборотам

## Зависимости

- `numpy` - математические операции
- `plotly` - создание 3D визуализации
- `functions.tube_command_generator` - генерация команд пробития
- `functions.motion_commands` - структуры команд движения

## Интеграция с GUI

Модуль интегрирован с основным GUI приложением через:
```python
from visualization import create_punch_visualization
```
