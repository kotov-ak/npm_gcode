#!/usr/bin/env python3
"""
Генератор G-кода"
Точка входа с выбором интерфейса.

Использование:
    python main.py              # Новый современный интерфейс (по умолчанию)
    python main.py --gui=new    # Новый современный интерфейс
    python main.py --gui=old    # Старый интерфейс (PyQt5)
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description='Генератор G-кода для иглопробивного станка'
    )
    parser.add_argument(
        '--gui',
        choices=['old', 'new'],
        default='new',
        help='Выбор интерфейса: old (PyQt5) или new (PySide6, по умолчанию)'
    )

    args = parser.parse_args()

    if args.gui == 'old':
        # Старый интерфейс на PyQt5
        from app.gui_app import app_show
        app_show()
    else:
        # Новый современный интерфейс на PySide6
        from app.modern_gui import app_show
        app_show()


if __name__ == '__main__':
    main()
