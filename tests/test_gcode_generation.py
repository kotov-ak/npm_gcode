#!/usr/bin/env python3
"""
Модуль тестирования G-code генератора
"""

import sys
import os
import unittest
import re
import time
from typing import List, Dict, Tuple

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.prod_functions import generate_command_lines


class TestGCodeGeneration(unittest.TestCase):
    """Тесты генерации G-code"""

    def setUp(self):
        """Настройка перед каждым тестом"""
        self.test_params = {
            'tube_len': 528,
            'i_diam': 60,
            'o_diam': 70,
            'fabric_thickness': 1,
            'punch_step_r': 1,
            'needle_step_X': 8,
            'needle_step_Y': 8,
            'volumetric_density': 25,
            'head_len': 264,
            'punch_depth': 15,
            'punch_offset': 10,
            'zero_offset_Y': 10,
            'zero_offset_Z': 0,
            'support_depth': 5,
            'idling_speed': 5000,
            'move_speed': 1000,
            'rotate_speed': 2000,
            'random_border':0.5,
            'num_of_needle_rows': 1,
            'x_substep_count': 8,
            'x_substep_count_in_one_revolution': 2,
        }

        self.reference_file = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'g_code_origin.txt'
        )

        # Допустимая погрешность для сравнения числовых параметров
        # Можно переопределить в конкретном тесте
        # Значение подобрано экспериментально для покрытия накопленной погрешности округления
        self.tolerance = 0.2

        # Параметры, которые проверяются с погрешностью (остальные должны совпадать точно)
        # По умолчанию только параметр A (угол поворота), т.к. он имеет накопленную погрешность
        self.tolerance_params = {'A'}

    def test_generation_matches_reference(self):
        """
        Интеграционный тест сравнения сгенерированного G-code с референсным файлом
        """
        print("\n=== ИНТЕГРАЦИОННЫЙ ТЕСТ СРАВНЕНИЯ С РЕФЕРЕНСНЫМ ФАЙЛОМ ===")

        # Проверяем, что референсный файл существует
        self.assertTrue(os.path.exists(self.reference_file),
                       f"Референсный файл не найден: {self.reference_file}")

        # Генерируем G-code
        print("Генерация G-code...")
        generated_lines = generate_command_lines(self.test_params)

        with open("last_test_2.txt", "w") as f:
            f.writelines(generated_lines)
        
        self.assertIsInstance(generated_lines, list, "Результат должен быть списком")
        self.assertGreater(len(generated_lines), 0, "Сгенерированный список не должен быть пустым")

        # Читаем референсный файл
        print("Чтение референсного файла...")
        with open(self.reference_file, 'r', encoding='utf-8') as f:
            reference_lines = [line.rstrip('\n') for line in f.readlines()]

        # Убираем переносы строк из сгенерированных данных для корректного сравнения
        generated_clean = [line.rstrip('\n') for line in generated_lines]

        print(f"Сгенерировано строк: {len(generated_clean)}")
        print(f"Референсных строк: {len(reference_lines)}")

        # Счетчики для предупреждений
        self.warnings_count = 0

        # Сравниваем структуру (игнорируем временные метки и статистику времени)
        self._compare_gcode_structure(generated_clean, reference_lines)

        # Сравниваем основные команды G-code (исключая заголовок)
        self._compare_gcode_commands(generated_clean, reference_lines)

        # Итоговый отчет
        self._print_final_report()

        print("\n✅ Тест сравнения прошел успешно!")

    def _compare_gcode_structure(self, generated: List[str], reference: List[str]):
        """Сравнение структуры G-code файлов"""

        # Найдем начало основных команд (после заголовка)
        gen_start_idx = self._find_commands_start(generated)
        ref_start_idx = self._find_commands_start(reference)

        self.assertGreater(gen_start_idx, 0, "Не найдено начало команд в сгенерированном файле")
        self.assertGreater(ref_start_idx, 0, "Не найдено начало команд в референсном файле")

        # Сравниваем заголовки (только как предупреждения)
        print("\n=== СРАВНЕНИЕ ЗАГОЛОВКОВ ===")
        self._compare_headers(generated[:gen_start_idx], reference[:ref_start_idx])

        # Сравниваем количество команд G-code (без заголовка)
        gen_commands = generated[gen_start_idx:]
        ref_commands = reference[ref_start_idx:]

        print(f"\nКоманд в сгенерированном файле: {len(gen_commands)}")
        print(f"Команд в референсном файле: {len(ref_commands)}")

        # Подробная диагностика различий
        self._detailed_command_analysis(gen_commands, ref_commands)

        # Проверяем параметры в заголовке
        self._verify_header_parameters(generated)

    def _compare_gcode_commands(self, generated: List[str], reference: List[str]):
        """Сравнение основных команд G-code"""

        gen_start_idx = self._find_commands_start(generated)
        ref_start_idx = self._find_commands_start(reference)

        gen_commands = [line for line in generated[gen_start_idx:] if line.strip() and not line.startswith(';')]
        ref_commands = [line for line in reference[ref_start_idx:] if line.strip() and not line.startswith(';')]

        # Инициализируем счетчики для статистики
        if not hasattr(self, 'tolerance_stats'):
            self.tolerance_stats = {
                'total_compared': 0,
                'exact_matches': 0,
                'within_tolerance': 0,
                'max_difference': 0.0,
                'max_difference_by_param': {},  # Макс разница для каждого параметра
                'differences': []
            }

        # Сравниваем все команды
        total_commands = min(len(gen_commands), len(ref_commands))

        for i in range(total_commands):
            gen_cmd = gen_commands[i].strip()
            ref_cmd = ref_commands[i].strip()

            # Сравниваем структуру команды
            self._compare_command_structure_with_stats(gen_cmd, ref_cmd, i)

        # Выводим статистику
        self._print_tolerance_statistics()

    def _compare_headers(self, gen_header: List[str], ref_header: List[str]):
        """Сравнение заголовков (выводит предупреждения, но не вызывает ошибки)"""

        warnings = []
        diff_lines_count = 0  # Счетчик различающихся строк

        # Проверяем размер заголовка
        if len(gen_header) != len(ref_header):
            warnings.append(f"Размер заголовка различается: {len(gen_header)} vs {len(ref_header)} строк")
            diff_lines_count += 1

        # Сравниваем построчно
        min_len = min(len(gen_header), len(ref_header))
        for i in range(min_len):
            if gen_header[i] != ref_header[i]:
                diff_lines_count += 1
                warnings.append(f"Строка {i+1} заголовка различается:")
                warnings.append(f"  Gen: {gen_header[i][:80]}")
                warnings.append(f"  Ref: {ref_header[i][:80]}")

        # Добавляем строки, которые есть только в одном из заголовков
        if len(gen_header) > min_len:
            diff_lines_count += (len(gen_header) - min_len)
        if len(ref_header) > min_len:
            diff_lines_count += (len(ref_header) - min_len)

        if warnings:
            # Добавляем количество различающихся строк в счетчик предупреждений
            self.warnings_count += diff_lines_count

            print("⚠️  ПРЕДУПРЕЖДЕНИЯ О РАЗЛИЧИЯХ В ЗАГОЛОВКЕ:")
            print(f"   Найдено различий в заголовке: {diff_lines_count} строк(и)")
            for warning in warnings[:15]:  # Ограничиваем вывод первыми 15 предупреждениями
                print(f"   {warning}")
            if len(warnings) > 15:
                print(f"   ... и еще {len(warnings) - 15} строк предупреждений")
        else:
            print("✅ Заголовки идентичны")

    def _parse_gcode_command(self, command: str) -> Tuple[str, Dict[str, float]]:
        """
        Парсит G-code команду, извлекая тип команды и параметры

        Args:
            command: строка G-code команды (например, "G01 X1.5 Y2.0 Z3.5 F1000")

        Returns:
            Кортеж (тип_команды, словарь_параметров)
            Например: ("G01", {"X": 1.5, "Y": 2.0, "Z": 3.5, "F": 1000.0})
        """
        # Удаляем комментарии
        clean_cmd = command.split(';')[0].strip()

        if not clean_cmd:
            return ("", {})

        parts = clean_cmd.split()
        if not parts:
            return ("", {})

        cmd_type = parts[0]
        params = {}

        # Парсим параметры (X123.45, Y67.89, и т.д.)
        for part in parts[1:]:
            match = re.match(r'([A-Z])(-?\d+\.?\d*)', part)
            if match:
                param_name = match.group(1)
                param_value = float(match.group(2))
                params[param_name] = param_value

        return (cmd_type, params)

    def _compare_params(self, gen_type: str, gen_params: Dict[str, float],
                       ref_type: str, ref_params: Dict[str, float],
                       tolerance: float, tolerance_params: set = None) -> Tuple[bool, str]:
        """
        Сравнивает распарсенные параметры команд с учетом погрешности

        Args:
            gen_type: тип сгенерированной команды
            gen_params: параметры сгенерированной команды
            ref_type: тип референсной команды
            ref_params: параметры референсной команды
            tolerance: допустимая погрешность для числовых параметров
            tolerance_params: набор параметров, для которых применяется погрешность.
                            Если None, погрешность применяется ко всем параметрам.
                            Остальные параметры должны совпадать точно.

        Returns:
            (True, "") если команды совпадают с учетом погрешности
            (False, сообщение_об_ошибке) в противном случае
        """
        # Проверяем тип команды
        if gen_type != ref_type:
            return (False, f"Тип команды различается: {gen_type} vs {ref_type}")

        # Проверяем наличие всех параметров
        if set(gen_params.keys()) != set(ref_params.keys()):
            missing_in_gen = set(ref_params.keys()) - set(gen_params.keys())
            missing_in_ref = set(gen_params.keys()) - set(ref_params.keys())
            msg = "Параметры различаются: "
            if missing_in_gen:
                msg += f"отсутствуют в gen: {missing_in_gen} "
            if missing_in_ref:
                msg += f"лишние в gen: {missing_in_ref}"
            return (False, msg)

        # Сравниваем значения параметров
        for param_name in gen_params:
            gen_value = gen_params[param_name]
            ref_value = ref_params[param_name]

            diff = abs(gen_value - ref_value)

            # Проверяем, нужно ли использовать погрешность для этого параметра
            use_tolerance = (tolerance_params is None) or (param_name in tolerance_params)

            if use_tolerance:
                # Сравниваем с погрешностью
                if diff > tolerance:
                    return (False,
                           f"Параметр {param_name} различается: {gen_value} vs {ref_value} "
                           f"(разница {diff:.6f} > допуск {tolerance})")
            else:
                # Требуем точного совпадения
                if diff > 0:
                    return (False,
                           f"Параметр {param_name} должен совпадать точно: {gen_value} vs {ref_value} "
                           f"(разница {diff:.6f})")

        return (True, "")

    def _compare_commands_with_tolerance(self, gen_cmd: str, ref_cmd: str,
                                         tolerance: float) -> Tuple[bool, str]:
        """
        Сравнивает две G-code команды с учетом погрешности для числовых параметров
        (обертка для обратной совместимости)

        Args:
            gen_cmd: сгенерированная команда
            ref_cmd: референсная команда
            tolerance: допустимая погрешность для числовых параметров

        Returns:
            (True, "") если команды совпадают с учетом погрешности
            (False, сообщение_об_ошибке) в противном случае
        """
        gen_type, gen_params = self._parse_gcode_command(gen_cmd)
        ref_type, ref_params = self._parse_gcode_command(ref_cmd)

        tolerance_params = getattr(self, 'tolerance_params', None)
        return self._compare_params(gen_type, gen_params, ref_type, ref_params,
                                   tolerance, tolerance_params)

    def _compare_command_structure_with_stats(self, gen_cmd: str, ref_cmd: str, line_num: int):
        """Сравнение команды с учетом статистики различий"""

        # Удаляем комментарии для сравнения
        gen_clean = gen_cmd.split(';')[0].strip()
        ref_clean = ref_cmd.split(';')[0].strip()

        # Проверяем различия в комментариях (выводим как предупреждение)
        gen_comment = gen_cmd.split(';', 1)[1].strip() if ';' in gen_cmd else ""
        ref_comment = ref_cmd.split(';', 1)[1].strip() if ';' in ref_cmd else ""

        if gen_comment != ref_comment:
            # Выводим только первые несколько различий в комментариях
            if not hasattr(self, 'comment_warnings_shown'):
                self.comment_warnings_shown = 0

            if self.comment_warnings_shown < 3:
                print(f"   ⚠️  Комментарии различаются в строке {line_num}:")
                print(f"      Gen: ;{gen_comment[:60]}")
                print(f"      Ref: ;{ref_comment[:60]}")
                self.comment_warnings_shown += 1
            elif self.comment_warnings_shown == 3:
                print(f"   ⚠️  ... (дальнейшие различия в комментариях не выводятся)")
                self.comment_warnings_shown += 1

            self.warnings_count += 1

        if gen_clean and ref_clean:
            self.tolerance_stats['total_compared'] += 1

            # Парсим команды один раз для подробного анализа
            gen_type, gen_params = self._parse_gcode_command(gen_clean)
            ref_type, ref_params = self._parse_gcode_command(ref_clean)

            # Проверяем точное совпадение
            if gen_clean == ref_clean:
                self.tolerance_stats['exact_matches'] += 1
                return

            # Сравниваем команды с учетом погрешности (используем уже распарсенные параметры)
            is_match, error_msg = self._compare_params(
                gen_type, gen_params, ref_type, ref_params, self.tolerance, self.tolerance_params
            )

            if is_match:
                # Совпадает в пределах погрешности
                self.tolerance_stats['within_tolerance'] += 1

                # Вычисляем максимальную разницу в параметрах
                for param_name in gen_params:
                    if param_name in ref_params:
                        diff = abs(gen_params[param_name] - ref_params[param_name])
                        if diff > 0:
                            self.tolerance_stats['max_difference'] = max(
                                self.tolerance_stats['max_difference'], diff
                            )

                            # Отслеживаем макс разницу для каждого параметра отдельно
                            if param_name not in self.tolerance_stats['max_difference_by_param']:
                                self.tolerance_stats['max_difference_by_param'][param_name] = diff
                            else:
                                self.tolerance_stats['max_difference_by_param'][param_name] = max(
                                    self.tolerance_stats['max_difference_by_param'][param_name], diff
                                )

                            self.tolerance_stats['differences'].append({
                                'line': line_num,
                                'param': param_name,
                                'diff': diff,
                                'gen': gen_params[param_name],
                                'ref': ref_params[param_name]
                            })
            else:
                # Различия вне допуска
                msg = f"Команда в строке {line_num} различается: {error_msg}\n"
                msg += f"  Gen: {gen_clean}\n"
                msg += f"  Ref: {ref_clean}"
                print(msg)
                self.fail(msg)

    def _compare_command_structure(self, gen_cmd: str, ref_cmd: str, line_num: int):
        """Сравнение структуры отдельной команды (без учета комментариев)"""

        # Удаляем комментарии для сравнения
        gen_clean = gen_cmd.split(';')[0].strip()
        ref_clean = ref_cmd.split(';')[0].strip()

        # Проверяем различия в комментариях (выводим как предупреждение)
        gen_comment = gen_cmd.split(';', 1)[1].strip() if ';' in gen_cmd else ""
        ref_comment = ref_cmd.split(';', 1)[1].strip() if ';' in ref_cmd else ""

        if gen_comment != ref_comment:
            # Выводим только первые несколько различий в комментариях
            if not hasattr(self, 'comment_warnings_shown'):
                self.comment_warnings_shown = 0

            if self.comment_warnings_shown < 3:
                print(f"   ⚠️  Комментарии различаются в строке {line_num}:")
                print(f"      Gen: ;{gen_comment[:60]}")
                print(f"      Ref: ;{ref_comment[:60]}")
                self.comment_warnings_shown += 1
            elif self.comment_warnings_shown == 3:
                print(f"   ⚠️  ... (дальнейшие различия в комментариях не выводятся)")
                self.comment_warnings_shown += 1

            self.warnings_count += 1

        if gen_clean and ref_clean:
            # Сравниваем команды с учетом погрешности
            is_match, error_msg = self._compare_commands(
                gen_clean, ref_clean, self.tolerance
            )

            if not is_match:
                self.fail(f"Команда в строке {line_num} различается: {error_msg}\n"
                         f"  Gen: {gen_clean}\n"
                         f"  Ref: {ref_clean}")

    def _find_commands_start(self, lines: List[str]) -> int:
        """
        Находит начало основных команд G-code (после заголовка)
        Ищет первую непустую строку, которая не является комментарием
        """
        for i, line in enumerate(lines):
            clean_line = line.strip()
            # Пропускаем пустые строки и комментарии
            if clean_line and not clean_line.startswith(';'):
                return i
        return -1

    def _verify_header_parameters(self, generated: List[str]):
        """Проверка параметров в заголовке"""
        header_text = '\n'.join(generated[:30])  # Первые 30 строк

        # Проверяем основные параметры
        self.assertIn('Tube length => 528', header_text, "Параметр tube_len не найден")
        self.assertIn('Internal diameter => 60', header_text, "Параметр i_diam не найден")
        self.assertIn('Outer diameter => 70', header_text, "Параметр o_diam не найден")
        self.assertIn('Volumetric density => 25', header_text, "Параметр volumetric_density не найден")

    def _print_tolerance_statistics(self):
        """Вывод статистики по погрешностям"""
        if not hasattr(self, 'tolerance_stats'):
            return

        stats = self.tolerance_stats
        print("\n" + "=" * 60)
        print("СТАТИСТИКА СРАВНЕНИЯ С ПОГРЕШНОСТЬЮ")
        print("=" * 60)

        total = stats['total_compared']
        exact = stats['exact_matches']
        within = stats['within_tolerance']

        print(f"Всего сравнено команд: {total}")
        print(f"Точное совпадение: {exact} ({100*exact/total:.1f}%)")
        print(f"Совпадение в пределах ±{self.tolerance}: {within} ({100*within/total:.1f}%)")

        if stats['max_difference'] > 0:
            print(f"\nОбщая максимальная разница: {stats['max_difference']:.6f}")

            # Показываем максимальную разницу по каждому параметру
            if stats['max_difference_by_param']:
                print("\nМаксимальные отклонения по параметрам:")
                for param, max_diff in sorted(stats['max_difference_by_param'].items()):
                    # Проверяем, применялась ли погрешность к этому параметру
                    with_tolerance = param in self.tolerance_params if self.tolerance_params else True
                    tolerance_mark = f" (с погрешностью ±{self.tolerance})" if with_tolerance else " (точное совпадение)"
                    print(f"  {param}: {max_diff:.6f}{tolerance_mark}")

            # Показываем топ-5 самых больших различий
            if stats['differences']:
                sorted_diffs = sorted(stats['differences'],
                                    key=lambda x: x['diff'], reverse=True)[:5]
                print("\nТоп-5 самых больших различий:")
                for i, diff_info in enumerate(sorted_diffs, 1):
                    print(f"  {i}. Строка {diff_info['line']}, параметр {diff_info['param']}: "
                          f"{diff_info['gen']} vs {diff_info['ref']} "
                          f"(разница {diff_info['diff']:.6f})")

        print("=" * 60)

    def _print_final_report(self):
        """Вывод итогового отчета о сравнении"""
        print("\n" + "=" * 60)
        print("ИТОГОВЫЙ ОТЧЕТ СРАВНЕНИЯ")
        print("=" * 60)

        # Формируем описание параметров с погрешностью
        if self.tolerance_params:
            tolerance_params_str = ', '.join(sorted(self.tolerance_params))
            print(f"Погрешность ±{self.tolerance} применяется к параметрам: {tolerance_params_str}")
            print("Остальные параметры требуют точного совпадения")
        else:
            print(f"Погрешность сравнения: ±{self.tolerance} (для всех параметров)")

        if self.warnings_count > 0:
            print(f"\n⚠️  Предупреждений: {self.warnings_count}")
            print("   (различия в заголовках и комментариях)")
        else:
            print("\n✅ Предупреждений нет")

        print("\nПРИМЕЧАНИЕ:")
        print("  - Различия в заголовках (временные метки, функции) - это нормально")
        print("  - Различия в комментариях после команд (;) - игнорируются")
        if self.tolerance_params:
            tolerance_params_str = ', '.join(sorted(self.tolerance_params))
            print(f"  - Параметры {tolerance_params_str} сравниваются с погрешностью ±{self.tolerance}")
            print("  - Остальные параметры (X, Y, Z, F и др.) требуют точного совпадения")
        else:
            print(f"  - Все числовые параметры сравниваются с погрешностью ±{self.tolerance}")
        print("  - Критичны только различия в типах команд и параметрах вне допуска")
        print("=" * 60)

    def _detailed_command_analysis(self, gen_commands: List[str], ref_commands: List[str]):
        """Подробный анализ различий в командах (игнорирует комментарии)"""
        print("\n=== ПОДРОБНЫЙ АНАЛИЗ РАЗЛИЧИЙ ===")

        # Фильтруем только G-code команды (без комментариев и пустых строк)
        # Удаляем комментарии из команд для корректного сравнения
        gen_gcode = []
        ref_gcode = []

        for line in gen_commands:
            stripped = line.strip()
            if stripped and not stripped.startswith(';'):
                # Берем только часть до комментария
                clean_cmd = stripped.split(';')[0].strip()
                if clean_cmd:
                    gen_gcode.append(clean_cmd)

        for line in ref_commands:
            stripped = line.strip()
            if stripped and not stripped.startswith(';'):
                # Берем только часть до комментария
                clean_cmd = stripped.split(';')[0].strip()
                if clean_cmd:
                    ref_gcode.append(clean_cmd)

        print(f"G-code команд в сгенерированном: {len(gen_gcode)}")
        print(f"G-code команд в референсном: {len(ref_gcode)}")

        # Анализ типов команд
        gen_command_types = {}
        ref_command_types = {}

        for cmd in gen_gcode:
            cmd_type = cmd.split()[0] if cmd.split() else "EMPTY"
            gen_command_types[cmd_type] = gen_command_types.get(cmd_type, 0) + 1

        for cmd in ref_gcode:
            cmd_type = cmd.split()[0] if cmd.split() else "EMPTY"
            ref_command_types[cmd_type] = ref_command_types.get(cmd_type, 0) + 1

        print("\nТипы команд в сгенерированном файле:")
        for cmd_type, count in sorted(gen_command_types.items()):
            print(f"  {cmd_type}: {count}")

        print("\nТипы команд в референсном файле:")
        for cmd_type, count in sorted(ref_command_types.items()):
            print(f"  {cmd_type}: {count}")

        # Найдем первое различие
        print("\nПоиск первого различия:")
        min_len = min(len(gen_gcode), len(ref_gcode))
        first_diff_idx = None

        for i in range(min_len):
            if gen_gcode[i] != ref_gcode[i]:
                first_diff_idx = i
                break

        if first_diff_idx is not None:
            print(f"Первое различие в команде #{first_diff_idx + 1}:")
            print(f"  Сгенерировано: {gen_gcode[first_diff_idx]}")
            print(f"  Ожидалось:     {ref_gcode[first_diff_idx]}")

            # Показываем контекст (±3 команды)
            start_idx = max(0, first_diff_idx - 3)
            end_idx = min(min_len, first_diff_idx + 4)

            print(f"\nКонтекст (команды {start_idx + 1}-{end_idx}):")
            for i in range(start_idx, end_idx):
                marker = " ❌ " if i == first_diff_idx else "    "
                if i < len(gen_gcode):
                    print(f"{marker}Gen {i+1:4d}: {gen_gcode[i]}")
                if i < len(ref_gcode):
                    print(f"    Ref {i+1:4d}: {ref_gcode[i]}")
                if i == first_diff_idx:
                    print()
        else:
            print("Первые команды идентичны до минимальной длины")

        # Если файлы разной длины, показываем где обрывается
        if len(gen_gcode) != len(ref_gcode):
            if len(gen_gcode) < len(ref_gcode):
                print(f"\nСгенерированный файл короче на {len(ref_gcode) - len(gen_gcode)} команд")
                print("Недостающие команды из референсного файла:")
                for i in range(len(gen_gcode), min(len(ref_gcode), len(gen_gcode) + 10)):
                    print(f"  Ref {i+1:4d}: {ref_gcode[i]}")
            else:
                print(f"\nСгенерированный файл длиннее на {len(gen_gcode) - len(ref_gcode)} команд")
                print("Лишние команды в сгенерированном файле:")
                for i in range(len(ref_gcode), min(len(gen_gcode), len(ref_gcode) + 10)):
                    print(f"  Gen {i+1:4d}: {gen_gcode[i]}")

        # Проверка на ожидаемое количество команд пробития (G01)
        gen_punch_count = gen_command_types.get('G01', 0)
        ref_punch_count = ref_command_types.get('G01', 0)

        if gen_punch_count != ref_punch_count:
            print(f"\n❌ Несоответствие количества команд пробития:")
            print(f"   Ожидалось: {ref_punch_count}")
            print(f"   Получено:  {gen_punch_count}")
            print(f"   Разность:  {gen_punch_count - ref_punch_count}")

        return first_diff_idx

    def test_generation_performance(self):
        """Тест производительности генерации"""
        print("\n=== ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ ===")

        start_time = time.time()
        generated_lines = generate_command_lines(self.test_params)
        end_time = time.time()

        generation_time = end_time - start_time

        print(f"Время генерации: {generation_time:.2f} секунд")
        print(f"Количество строк: {len(generated_lines)}")
        print(f"Производительность: {len(generated_lines) / generation_time:.0f} строк/сек")

        # Проверяем, что генерация не занимает слишком много времени
        self.assertLess(generation_time, 30.0, "Генерация занимает слишком много времени")
        self.assertGreater(len(generated_lines), 1000, "Слишком мало сгенерированных строк")


if __name__ == '__main__':
    # Запуск тестов напрямую из этого файла
    unittest.main(verbosity=2)
