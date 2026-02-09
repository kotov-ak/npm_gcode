"""
Утилиты для работы с файлами.
Определение путей для Windows и Linux.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional


def get_desktop_path() -> Optional[Path]:
    """
    Получить путь к рабочему столу для Windows и Linux.
    Возвращает None если рабочий стол не найден.
    """
    if os.name == 'nt':  # Windows
        # Используем USERPROFILE для Windows
        user_profile = os.environ.get('USERPROFILE')
        if user_profile:
            desktop = Path(user_profile) / 'Desktop'
            if desktop.exists():
                return desktop
            # Попробуем локализованное имя (Рабочий стол)
            desktop_ru = Path(user_profile) / 'Рабочий стол'
            if desktop_ru.exists():
                return desktop_ru
    else:  # Linux/Mac
        # Попробуем XDG_DESKTOP_DIR
        try:
            # Читаем user-dirs.dirs
            user_dirs_file = Path.home() / '.config' / 'user-dirs.dirs'
            if user_dirs_file.exists():
                with open(user_dirs_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('XDG_DESKTOP_DIR'):
                            # Формат: XDG_DESKTOP_DIR="$HOME/Desktop"
                            path_str = line.split('=')[1].strip().strip('"')
                            path_str = path_str.replace('$HOME', str(Path.home()))
                            desktop = Path(path_str)
                            if desktop.exists():
                                return desktop
        except Exception:
            pass

        # Fallback на стандартные пути
        for desktop_name in ['Desktop', 'Рабочий стол']:
            desktop = Path.home() / desktop_name
            if desktop.exists():
                return desktop

    return None


def get_executable_dir() -> Path:
    """
    Получить директорию исполняемого файла или скрипта.
    Работает как для скрипта, так и для скомпилированного exe.
    """
    if getattr(sys, 'frozen', False):
        # Запуск как скомпилированный exe (PyInstaller)
        return Path(sys.executable).parent
    else:
        # Запуск как Python скрипт
        # Возвращаем корневую директорию проекта (npm_gcode)
        return Path(__file__).parent.parent.parent


def get_save_path(filename: str, save_to_desktop: bool = False) -> Path:
    """
    Получить полный путь для сохранения файла.

    Args:
        filename: Имя файла без расширения
        save_to_desktop: Сохранять на рабочий стол

    Returns:
        Полный путь к файлу с расширением .txt
    """
    # Очистить имя файла от недопустимых символов
    invalid_chars = "'/:*?\"<>+|\\"
    clean_filename = ''.join(c for c in filename if c not in invalid_chars)

    if not clean_filename:
        clean_filename = "gcode_output"

    if save_to_desktop:
        desktop = get_desktop_path()
        if desktop:
            return desktop / f"{clean_filename}.txt"

    # Fallback на директорию исполняемого файла
    return get_executable_dir() / f"{clean_filename}.txt"


def validate_filename(filename: str) -> tuple[bool, Optional[str]]:
    """
    Проверить корректность имени файла.

    Returns:
        (is_valid, error_char) - кортеж с флагом валидности и недопустимым символом
    """
    invalid_chars = "'/:*?\"<>+|\\"
    for char in filename:
        if char in invalid_chars:
            return False, char
    return True, None
