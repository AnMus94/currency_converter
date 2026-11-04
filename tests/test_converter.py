"""
Тесты для модуля конвертации валют.
"""

import requests
import pytest
from unittest.mock import patch, MagicMock
from converter import convert_currency, get_exchange_rates
from exceptions import InvalidAmountError, UnsupportedCurrencyError, APIConnectionError


class TestConvertCurrency:
    """Тесты функции конвертации валют."""
    
    @patch('converter.get_exchange_rates')
    def test_convert_usd_to_rub(self, mock_get_rates):
        """Тест конвертации USD в RUB."""
        # Мокаем ответ API: 1 USD = 92.5 RUB
        mock_get_rates.return_value = {'RUB': 92.5, 'EUR': 0.85}
        
        result = convert_currency(100, 'USD', 'RUB')
        
        assert result == 9250.0
        mock_get_rates.assert_called_once_with('USD')
    
    @patch('converter.get_exchange_rates')
    def test_convert_zero_amount(self, mock_get_rates):
        """Тест конвертации нулевой суммы (должна вызвать ошибку)."""
        with pytest.raises(InvalidAmountError):
            convert_currency(0, 'USD', 'RUB')
    
    @patch('converter.get_exchange_rates')
    def test_convert_negative_amount(self, mock_get_rates):
        """Тест конвертации отрицательной суммы (должна вызвать ошибку)."""
        with pytest.raises(InvalidAmountError):
            convert_currency(-50, 'USD', 'RUB')
    
    @patch('converter.get_exchange_rates')
    def test_unsupported_currency(self, mock_get_rates):
        """Тест конвертации в неподдерживаемую валюту."""
        mock_get_rates.return_value = {'RUB': 92.5, 'EUR': 0.85}
        
        with pytest.raises(UnsupportedCurrencyError):
            convert_currency(100, 'USD', 'XYZ')
    
    @patch('converter.get_exchange_rates')
    def test_convert_eur_to_usd(self, mock_get_rates):
        """Тест конвертации EUR в USD."""
        mock_get_rates.return_value = {'USD': 1.10, 'RUB': 101.5}
        
        result = convert_currency(50, 'EUR', 'USD')
        
        assert result == 55.0


class TestGetExchangeRates:
    """Тесты функции получения курсов валют."""
    
    @patch('converter.requests.get')
    @patch('converter.load_cache')
    def test_get_rates_from_api(self, mock_load_cache, mock_requests_get):
        """Тест получения курсов из API (когда кэш пуст)."""
        # Мокаем отсутствие кэша
        mock_load_cache.return_value = None
        
        # Мокаем ответ API
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'result': 'success',
            'rates': {'USD': 1.0, 'RUB': 92.5, 'EUR': 0.85}
        }
        mock_response.raise_for_status = MagicMock()
        mock_requests_get.return_value = mock_response
        
        with patch('converter.save_cache'):  # Мокаем сохранение в кэш
            rates = get_exchange_rates('USD')
        
        assert rates == {'USD': 1.0, 'RUB': 92.5, 'EUR': 0.85}
        mock_requests_get.assert_called_once()
    
    @patch('converter.load_cache')
    def test_get_rates_from_cache(self, mock_load_cache):
        """Тест получения курсов из кэша."""
        mock_load_cache.return_value = {'RUB': 92.5, 'EUR': 0.85}
        
        with patch('converter.requests.get') as mock_get:
            rates = get_exchange_rates('USD')
            
            # Проверяем, что API не вызывался (взяли из кэша)
            mock_get.assert_not_called()
            assert rates == {'RUB': 92.5, 'EUR': 0.85}
    
    @patch('converter.requests.get')
    @patch('converter.load_cache')
    def test_api_connection_error(self, mock_load_cache, mock_requests_get):
        """Тест ошибки соединения с API."""
        mock_load_cache.return_value = None
        # Имитируем именно ту ошибку, которую выбрасывает библиотека requests при сбое сети
        mock_requests_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(APIConnectionError):
            get_exchange_rates('USD')