"""
Тесты для модуля кэширования.
"""

import pytest
import json
import os
import time
from unittest.mock import patch, mock_open
from cache import load_cache, save_cache, CACHE_TTL
from exceptions import CacheError


class TestCache:
    """Тесты функций кэширования."""
    
    @patch('cache.os.path.exists')
    def test_load_cache_file_not_exists(self, mock_exists):
        """Тест загрузки из несуществующего файла."""
        mock_exists.return_value = False
        
        result = load_cache('USD')
        
        
        assert result is None
    
    @patch('cache.time.time')
    @patch('cache.os.path.exists')
    @patch('cache.open', new_callable=mock_open, read_data='{"USD": {"rates": {"RUB": 92.5}, "timestamp": 1000}}')
    def test_load_cache_valid(self, mock_file, mock_exists, mock_time):
        """Тест успешной загрузки актуального кэша."""
        mock_exists.return_value = True
        mock_time.return_value = 1000 + 100  # Прошло 100 секунд (меньше TTL)
        
        result = load_cache('USD')
        
        assert result == {'RUB': 92.5}
    
    @patch('cache.time.time')
    @patch('cache.os.path.exists')
    @patch('cache.open', new_callable=mock_open, read_data='{"USD": {"rates": {"RUB": 92.5}, "timestamp": 1000}}')
    def test_load_cache_expired(self, mock_file, mock_exists, mock_time):
        """Тест загрузки устаревшего кэша (должен вернуть None)."""
        mock_exists.return_value = True
        mock_time.return_value = 1000 + CACHE_TTL + 1  # Прошло больше чем TTL
        
        result = load_cache('USD')
        
        assert result is None
    
    @patch('cache.os.path.exists')
    @patch('cache.open', new_callable=mock_open)
    def test_save_cache_new_file(self, mock_file, mock_exists):
        """Тест сохранения в новый файл."""
        mock_exists.return_value = False
        
        with patch('cache.time.time', return_value=1000):
            with patch('cache.json.dump') as mock_dump:
                save_cache('USD', {'RUB': 92.5})
                
                # Проверяем, что json.dump был вызван
                assert mock_dump.called
    
    @patch('cache.open', new_callable=mock_open, read_data='{}')
    def test_save_cache_corrupted_file(self, mock_file):
        """Тест сохранения при поврежденном файле кэша."""
        with patch('cache.json.load', side_effect=json.JSONDecodeError('msg', 'doc', 0)):
            with patch('cache.time.time', return_value=1000):
                # Не должно вызвать ошибку, а создать новый кэш
                save_cache('USD', {'RUB': 92.5})