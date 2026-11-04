"""
Главный файл приложения. Точка входа и консольный интерфейс.
"""

from logger_setup import setup_logger
from converter import convert_currency
from exceptions import CurrencyConverterError

def main():
    # Запускаем настройку логирования
    setup_logger()

    print("=" * 40)
    print("=== Программа конвертации валют ===")
    print("=" * 40)
    print("Для выхода введите 'exit' в поле суммы.\n")

    while True:
        # 1. Ввод суммы
        amount_str = input("Введите сумму для конвертации (или 'exit' для выхода): ").strip()
        
        if amount_str.lower() == 'exit':
            print("Завершение работы программы. До свидания!")
            break

        # 2. Ввод валют
        from_currency = input("Введите исходную валюту (например, USD): ").strip()
        to_currency = input("Введите целевую валюту (например, RUB): ").strip()

        # 3. Обработка и конвертация
        try:
            # Пытаемся преобразовать ввод в число
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError("Сумма должна быть больше нуля")

            # Вызов основной функции конвертации
            result = convert_currency(amount, from_currency, to_currency)
            
            # Красивый вывод результата
            print(f"\n✅ Результат: {amount} {from_currency.upper()} = {result} {to_currency.upper()}\n")

        except ValueError:
            # Ловим ошибки ввода (не число, отрицательное число)
            print("\n❌ Ошибка ввода: Пожалуйста, введите корректное положительное число.\n")
            
        except CurrencyConverterError as e:
            # Ловим все наши кастомные исключения (ошибки API, кэша, валюты)
            print(f"\n❌ Ошибка конвертации: {e}\n")
            
        except Exception as e:
            # Ловим любые другие непредвиденные ошибки
            print(f"\n❌ Произошла непредвиденная ошибка: {e}\n")

if __name__ == "__main__":
    main()