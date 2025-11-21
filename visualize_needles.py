#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт для быстрой визуализации позиций игл с пользовательскими параметрами
"""

import argparse
from visualization import create_needle_visualization

def main():
    parser = argparse.ArgumentParser(
        description='Визуализация позиций игл иглопробивного станка'
    )
    parser.add_argument(
        '--needle-step-x',
        type=float,
        default=8,
        help='Расстояние между иглами вдоль оси X (мм), по умолчанию: 8'
    )
    parser.add_argument(
        '--needle-step-y',
        type=float,
        default=8,
        help='Расстояние между иглами вдоль оси Y (мм), по умолчанию: 8'
    )
    parser.add_argument(
        '--head-len',
        type=float,
        default=264,
        help='Максимальная длина иглопробивной головки (мм), по умолчанию: 264'
    )
    parser.add_argument(
        '--rows',
        type=int,
        default=1,
        help='Количество рядов игл вдоль оси Y, по умолчанию: 1'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='needle_positions.html',
        help='Имя выходного HTML файла, по умолчанию: needle_positions.html'
    )
    parser.add_argument(
        '--no-open',
        action='store_true',
        help='Не открывать визуализацию в браузере автоматически'
    )

    args = parser.parse_args()

    print("=" * 80)
    print("ВИЗУАЛИЗАЦИЯ ПОЗИЦИЙ ИГЛ")
    print("=" * 80)
    print(f"\nПараметры:")
    print(f"  needle_step_X: {args.needle_step_x} мм")
    print(f"  needle_step_Y: {args.needle_step_y} мм")
    print(f"  head_len: {args.head_len} мм")
    print(f"  num_of_needle_rows: {args.rows}")
    print(f"  output_file: {args.output}")
    print()

    fig, warning, warning_message = create_needle_visualization(
        needle_step_X=args.needle_step_x,
        needle_step_Y=args.needle_step_y,
        head_len=args.head_len,
        num_of_needle_rows=args.rows,
        output_file=args.output,
        auto_open=not args.no_open
    )

    if warning:
        print(f"\n{warning_message}\n")

    print("=" * 80)
    print("ВИЗУАЛИЗАЦИЯ ЗАВЕРШЕНА")
    print("=" * 80)

if __name__ == "__main__":
    main()
