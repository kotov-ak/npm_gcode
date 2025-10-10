#!/usr/bin/env python3
"""
Скрипт для запуска всех тестов проекта
"""

import sys
import os

# Добавляем родительский каталог в путь для импорта модулей
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from tests.test_runner import TestRunner


def main():
    """Основная функция запуска тестов"""
    print("🧪 ЗАПУСК ТЕСТОВ ГЕНЕРАТОРА G-CODE")
    print("=" * 50)

    try:
        # Запускаем все тесты
        success = TestRunner.run_all_tests()

        if success:
            print("\n🎉 ВСЕ ТЕСТЫ ПРОШЛИ УСПЕШНО!")
            print("✅ Генератор работает корректно")
            return 0
        else:
            print("\n❌ НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛИЛИСЬ!")
            print("⚠️  Требуется исправление")
            return 1

    except Exception as e:
        print(f"\n💥 ОШИБКА ПРИ ЗАПУСКЕ ТЕСТОВ: {e}")
        return 1


if __name__ == '__main__':
    sys.exit(main())