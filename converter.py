"""
Модуль основной логики конвертации валют.

Отвечает за получение курсов через API, использование кэша
и непосредственный расчет конвертации.
"""

import logging
import requests
from exceptions import (
    APIConnectionError,
    InvalidAmountError,
    ParsingError,
    UnsupportedCurrencyError
)
from cache import load_cache, save_cache

# Настройка логгера для этого модуля
logger = logging.getLogger(__name__)

# URL бесплатного API для получения курсов валют (не требует API-ключа)
API_URL = "https://open.er-api.com/v6/latest/{base_currency}"


def get_exchange_rates(base_currency: str) -> dict:
    """
    Получает актуальные курсы валют относительно базовой валюты.
    
    Сначала проверяет кэш. Если данные устарели или отсутствуют,
    делает запрос к внешнему API.
    
    Args:
        base_currency: Код базовой валюты (например, 'USD').
        
    Returns:
        Словарь с кодами валют и их курсами относительно base_currency.
    """
    base_currency = base_currency.upper()
    logger.info(f"Запрос курсов для базовой валюты: {base_currency}")
    
    # 1. Пытаемся получить данные из кэша
    rates = load_cache(base_currency)
    if rates:
        logger.info(f"Курсы для {base_currency} успешно получены из кэша.")
        return rates
        
    # 2. Если в кэше нет, делаем запрос к API
    logger.info("Данные в кэше отсутствуют или устарели. Запрос к API...")
    try:
        response = requests.get(API_URL.format(base_currency=base_currency), timeout=10)
        response.raise_for_status()  # Вызовет HTTPError, если статус не 200 OK
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Ошибка сети при запросе к API: {e}")
        raise APIConnectionError(f"Не удалось подключиться к API: {e}")
        
    # 3. Парсим JSON-ответ
    try:
        data = response.json()
        if data.get("result") != "success" or "rates" not in data:
            raise ValueError("Неверная структура ответа API")
        rates = data["rates"]
        
    except (ValueError, KeyError, requests.exceptions.JSONDecodeError) as e:
        logger.error(f"Ошибка парсинга JSON от API: {e}")
        raise ParsingError(f"Не удалось обработать ответ API: {e}")
        
    # 4. Сохраняем свежие данные в кэш
    save_cache(base_currency, rates)
    logger.info(f"Курсы для {base_currency} сохранены в кэш.")
    
    return rates


def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Конвертирует сумму из одной валюты в другую.
    
    Args:
        amount: Сумма для конвертации.
        from_currency: Код валюты исходной суммы (например, 'USD').
        to_currency: Код целевой валюты (например, 'RUB').
        
    Returns:
        Конвертированная сумма (округленная до 2 знаков).
    """
    # Валидация суммы
    if not isinstance(amount, (int, float)) or amount <= 0:
        logger.warning(f"Попытка конвертации некорректной суммы: {amount}")
        raise InvalidAmountError(f"Сумма должна быть положительным числом, получено: {amount}")
        
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    
    logger.info(f"Начало конвертации: {amount} {from_currency} -> {to_currency}")
    
    # Получаем курсы для исходной валюты
    rates = get_exchange_rates(from_currency)
    
    # Проверяем, поддерживается ли целевая валюта
    if to_currency not in rates:
        logger.error(f"Целевая валюта {to_currency} не найдена в курсах API.")
        raise UnsupportedCurrencyError(
            currency=to_currency, 
            message=f"Валюта '{to_currency}' не поддерживается или не найдена."
        )
        
    # Расчет конвертации
    # API возвращает курсы относительно базовой валюты. 
    # Например, если base=USD, то rates['RUB'] = 92.5.
    # Значит, 1 USD = 92.5 RUB.
    converted_amount = amount * rates[to_currency]
    
    logger.info(f"Конвертация успешна: {amount} {from_currency} = {converted_amount:.2f} {to_currency}")
    
    return round(converted_amount, 2)