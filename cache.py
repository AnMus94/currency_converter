"""
Модуль для кэширования курсов валют.

Сохраняет и загружает курсы валют в JSON-файл, чтобы уменьшить
количество запросов к API и обеспечить работу приложения без интернета.
"""

import json
import os
import time
from exceptions import CacheError

# Имя файла, в котором будет храниться кэш
CACHE_FILE = "currency_cache.json"

# Время жизни кэша в секундах (1 час = 3600 секунд)
CACHE_TTL = 3600


def load_cache(base_currency: str) -> dict | None:
    """
    Загружает курсы валют из кэш-файла.
    
    Проверяет, существует ли файл и не истекло ли время жизни кэша.
    
    Args:
        base_currency: Базовая валюта, курсы которой нужно получить (например, 'USD').
        
    Returns:
        Словарь с курсами валют, если кэш актуален, иначе None.
    """
    # Если файла кэша вообще нет, возвращаем None
    if not os.path.exists(CACHE_FILE):
        return None
        
    try:
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
            
        # Проверяем, есть ли данные для нужной базовой валюты
        if base_currency in cache_data:
            cached_entry = cache_data[base_currency]
            current_time = time.time()
            
            # Проверяем, не истекло ли время жизни кэша
            if current_time - cached_entry['timestamp'] < CACHE_TTL:
                return cached_entry['rates']
                
    except (json.JSONDecodeError, IOError, KeyError) as e:
        # Если файл повреждён или произошла ошибка чтения, вызываем наше исключение
        raise CacheError(f"Ошибка при чтении кэша: {e}")
        
    return None


def save_cache(base_currency: str, rates: dict) -> None:
    """
    Сохраняет курсы валют в кэш-файл.
    
    Если файл уже существует, обновляет данные для указанной валюты,
    не удаляя данные для других валют.
    
    Args:
        base_currency: Базовая валюта (например, 'USD').
        rates: Словарь с актуальными курсами валют.
    """
    cache_data = {}
    
    # Пытаемся прочитать существующий файл, чтобы не перезаписать другие валюты
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
        except (json.JSONDecodeError, IOError):
            # Если файл повреждён, просто начинаем с пустого словаря
            cache_data = {}

    # Добавляем или обновляем данные для текущей валюты
    cache_data[base_currency] = {
        'rates': rates,
        'timestamp': time.time()
    }
    
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        raise CacheError(f"Ошибка при записи в кэш: {e}")