#!/usr/bin/env python3
"""
Запуск всех тестов проекта
"""

import sys
import os
import unittest

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_gcode_generation import TestGCodeGeneration
from tests.test_basic_functionality import TestBasicFunctionality
from tests.test_gui import TestGUI


class TestRunner:
    """Запуск тестов"""

    @staticmethod
    def run_all_tests():
        """
        Запуск всех тестов в правильном порядке:
        1. Базовые тесты функциональности
        2. Тест производительности
        3. GUI smoke test
        4. Интеграционный тест (последний)
        """
        suite = unittest.TestSuite()

        # 1. Добавляем базовые тесты функциональности (быстрые unit-тесты)
        try:
            loader = unittest.TestLoader()
            suite.addTests(loader.loadTestsFromTestCase(TestBasicFunctionality))
        except ImportError:
            print("⚠️  Базовые тесты не найдены, пропускаем...")

        # 2. Добавляем тест производительности
        try:
            suite.addTest(TestGCodeGeneration('test_generation_performance'))
        except Exception as e:
            print(f"⚠️  Тест производительности не найден: {e}")

        # 3. Добавляем интеграционный тест (последним, т.к. самый долгий)
        try:
            suite.addTest(TestGCodeGeneration('test_generation_matches_reference'))
        except Exception as e:
            print(f"⚠️  Интеграционный тест не найден: {e}")

        # 4. Добавляем GUI тесты (smoke test)
        try:
            suite.addTest(TestGUI('test_gui_application_launch'))
        except ImportError:
            print("⚠️  GUI тесты не найдены, пропускаем...")

        # Запускаем тесты
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)

        return result.wasSuccessful()


if __name__ == '__main__':
    print("🧪 ЗАПУСК ТЕСТОВ ГЕНЕРАТОРА G-CODE")
    print("=" * 50)

    success = TestRunner.run_all_tests()

    if success:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
        print("✅ Генератор работает корректно")
        sys.exit(0)
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
        print("⚠️  Требуется исправление")
        sys.exit(1)
