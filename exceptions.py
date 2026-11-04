"""
Модуль обработки исключений для приложения конвертации валют.

Содержит кастомные классы исключений для обработки различных ошибок,
которые могут возникнуть при работе с API, кэшем и валидации данных.
"""


class CurrencyConverterError(Exception):
    """
    Базовый класс для всех исключений конвертера валют.
    
    Используется как родительский класс для специфичных ошибок,
    что позволяет перехватывать все ошибки конвертера одним блоком except.
    
    Пример использования:
        try:
            convert_currency(100, "USD", "RUB")
        except CurrencyConverterError as e:
            print(f"Ошибка конвертера: {e}")
    """
    
    def __init__(self, message: str = "Произошла ошибка в конвертере валют") -> None:
        """
        Инициализация базового исключения.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки.
        
        Returns:
            Форматированное сообщение об ошибке
        """
        return f"[CurrencyConverterError]: {self.message}"


class APIConnectionError(CurrencyConverterError):
    """
    Исключение при ошибке соединения с API курсов валют.
    
    Вызывается когда:
    - Отсутствует интернет-соединение
    - API-сервер недоступен или вернул ошибку (5xx, 4xx)
    - Превышено время ожидания ответа (timeout)
    - DNS не может разрешить адрес API
    
    Пример использования:
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
        except requests.RequestException:
            raise APIConnectionError("Не удалось подключиться к API")
    """
    
    def __init__(self, message: str = "Ошибка соединения с API курсов валют. Проверьте интернет-соединение.") -> None:
        """
        Инициализация ошибки соединения с API.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки соединения.
        
        Returns:
            Форматированное сообщение об ошибке API
        """
        return f"[APIConnectionError]: {self.message}"


class InvalidAmountError(CurrencyConverterError):
    """
    Исключение при вводе некорректной суммы для конвертации.
    
    Вызывается когда:
    - Сумма отрицательная (меньше нуля)
    - Сумма равна нулю
    - Введено не число (строка, None, и т.д.)
    - Сумма превышает допустимый диапазон
    
    Пример использования:
        if amount <= 0:
            raise InvalidAmountError(f"Сумма должна быть положительной, получено: {amount}")
    """
    
    def __init__(self, message: str = "Неверно введённая сумма. Сумма должна быть положительным числом.") -> None:
        """
        Инициализация ошибки некорректной суммы.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки суммы.
        
        Returns:
            Форматированное сообщение об ошибке валидации суммы
        """
        return f"[InvalidAmountError]: {self.message}"


class UnsupportedCurrencyError(CurrencyConverterError):
    """
    Исключение при использовании неподдерживаемой валюты.
    
    Вызывается когда:
    - Валюта не найдена в списке доступных валют API
    - Код валюты введён с ошибкой (например, "USS" вместо "USD")
    - Валюта не поддерживается выбранным API
    
    Пример использования:
        if currency_code not in available_currencies:
            raise UnsupportedCurrencyError(f"Валюта '{currency_code}' не поддерживается")
    """
    
    def __init__(self, currency: str = "", message: str = "Неподдерживаемая валюта.") -> None:
        """
        Инициализация ошибки неподдерживаемой валюты.
        
        Args:
            currency: Код неподдерживаемой валюты (например, "XYZ")
            message: Текст сообщения об ошибке
        """
        self.currency = currency
        if currency:
            self.message = f"{message} Код валюты: '{currency}'"
        else:
            self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки валюты.
        
        Returns:
            Форматированное сообщение об ошибке unsupported currency
        """
        return f"[UnsupportedCurrencyError]: {self.message}"


class CacheError(CurrencyConverterError):
    """
    Исключение при ошибке чтения или записи кэша.
    
    Вызывается когда:
    - Файл кэша повреждён или не является валидным JSON
    - Нет прав на запись в файл кэша
    - Диск заполнен и невозможно записать данные
    - Файл кэша заблокирован другим процессом
    
    Пример использования:
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            raise CacheError(f"Ошибка чтения кэша: {e}")
    """
    
    def __init__(self, message: str = "Ошибка чтения/записи кэша.") -> None:
        """
        Инициализация ошибки кэша.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки кэша.
        
        Returns:
            Форматированное сообщение об ошибке кэширования
        """
        return f"[CacheError]: {self.message}"


class ParsingError(CurrencyConverterError):
    """
    Исключение при ошибке парсинга JSON-ответа от API.
    
    Вызывается когда:
    - API вернул не JSON (например, HTML страницу ошибки)
    - JSON повреждён или имеет неверную структуру
    - Отсутствуют ожидаемые поля в ответе API
    - Данные в JSON имеют неверный тип (например, строка вместо числа)
    
    Пример использования:
        try:
            data = response.json()
            if 'rates' not in data:
                raise ParsingError("Отсутствует поле 'rates' в ответе API")
        except ValueError as e:
            raise ParsingError(f"Ошибка парсинга JSON: {e}")
    """
    
    def __init__(self, message: str = "Ошибка парсинга JSON-ответа от API.") -> None:
        """
        Инициализация ошибки парсинга.
        
        Args:
            message: Текст сообщения об ошибке
        """
        self.message = message
        super().__init__(self.message)
    
    def __str__(self) -> str:
        """
        Возвращает строковое представление ошибки парсинга.
        
        Returns:
            Форматированное сообщение об ошибке парсинга JSON
        """
        return f"[ParsingError]: {self.message}"