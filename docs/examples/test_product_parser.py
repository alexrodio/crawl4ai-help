import pytest
from unittest.mock import AsyncMock, patch
from crawl4ai import AsyncWebCrawler
from amazon_product_extraction_direct_url import extract_amazon_products  # Замените your_module на имя вашего файла
import json
#todo нихера не понимаю

C:/Users/alalr/anaconda3/envs/CRAWL4Ai/python.exe "
@pytest.mark.asyncio
@patch('crawl4ai.AsyncWebCrawler')
async def test_successful_parsing(mock_crawler):
    # Мокаем ответ краулера
    mock_response = AsyncMock()
    mock_response.extracted_content = json.dumps([{
        "title": "Test Product",
        "price": "1000 ₽",
        "compatibility": ["Item1", "Item2"]
    }])

    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_response)

    # Запускаем тестируемую функцию
    await extract_amazon_products()

    # Проверяем вызовы
    mock_crawler.return_value.arun.assert_awaited_once()


@pytest.mark.asyncio
@patch('crawl4ai.AsyncWebCrawler')
async def test_empty_response(mock_crawler):
    mock_response = AsyncMock()
    mock_response.extracted_content = None
    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_response)

    await extract_amazon_products()


@pytest.mark.asyncio
@patch('crawl4ai.AsyncWebCrawler')
async def test_invalid_json(mock_crawler):
    mock_response = AsyncMock()
    mock_response.extracted_content = "INVALID JSON"
    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_response)

    await extract_amazon_products()


def test_field_selectors():
    schema = extract_amazon_products.__closure__[0].cell_contents.crawler_config.extraction_strategy.schema
    assert schema['baseSelector'] == "div.site-content-container"
    assert any(field['name'] == 'price' for field in schema['fields'])

# Добавьте другие тесты по аналогии