"""
Модуль настройки логирования.

Настраивает логгер для записи событий как в консоль, 
так и в файл для последующего анализа.
"""

import logging

def setup_logger(log_file: str = "converter.log") -> None:
    """
    Инициализирует и настраивает глобальный логгер.
    
    Args:
        log_file: Имя файла, в который будут записываться логи.
    """
    # Получаем корневой логгер
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Формат сообщения: Время - Имя_модуля - Уровень - Сообщение
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 1. Обработчик для записи в файл
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # 2. Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру (проверяем, чтобы не дублировать при повторном вызове)
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)