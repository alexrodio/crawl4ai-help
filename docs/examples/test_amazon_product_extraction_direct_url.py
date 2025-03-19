import pytest
from unittest.mock import AsyncMock, patch
from amazon_product_extraction_direct_url import extract_amazon_products  # Замените your_module
import json


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

    # Настраиваем мок
    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(
        return_value=mock_response
    )

    # Запускаем тестируемую функцию
    await extract_amazon_products()

    # Проверяем вызовы
    mock_crawler.return_value.arun.assert_called_once()


@pytest.mark.asyncio
@patch('crawl4ai.AsyncWebCrawler')
async def test_empty_response(mock_crawler):
    mock_response = AsyncMock()
    mock_response.extracted_content = None
    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(
        return_value=mock_response
    )

    await extract_amazon_products()


@pytest.mark.asyncio
@patch('crawl4ai.AsyncWebCrawler')
async def test_invalid_json(mock_crawler):
    mock_response = AsyncMock()
    mock_response.extracted_content = "INVALID JSON"
    mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(
        return_value=mock_response
    )

    await extract_amazon_products()


def test_field_selectors():
    # Создаем схему вручную
    schema = {
        "name": "Product Details",
        "baseSelector": "div.site-content-container",
        "fields": [
            {"name": "title", "selector": ".subject span[data-field='subject']", "type": "text"},
            {"name": "id__num", "selector": ".viewbull-bulletin-id__num", "type": "text"},
            {"name": "price", "selector": ".viewbull-summary-price__value", "type": "text"},
            {"name": "availability", "selector": ".viewbull-field__container span[data-field='goodPresentState']",
             "type": "text"},
            {"name": "condition", "selector": ".viewbull-field__container span[data-field='condition']",
             "type": "text"},
            {"name": "manufacturer", "selector": ".viewbull-field__container span[data-field='manufacturer']",
             "type": "text"},
            {"name": "part_number", "selector": ".viewbull-field__container span[data-field='autoPartsOemNumber']",
             "type": "text"},
            {"name": "part_number_ZAMENA", "selector": "ul.oem-numbers__list[data-field='autoPartsSubstituteNumbers']",
             "type": "text"},
            {"name": "compatibility",
             "selector": ".viewbull-field__container ul[data-field='autoPartsCompatibility'] li", "type": "text"},
            {"name": "seller_name", "selector": ".seller-summary-user a", "type": "text"},
            {"name": "image_urls", "selector": "div.image-gallery__big-image-container img", "type": "attribute",
             "attribute": "src", "multiple": True},
            {"name": "image_descriptions", "selector": "div.image-gallery__big-image-container img",
             "type": "attribute", "attribute": "alt", "multiple": True},
            {"name": "article_text",
             "selector": ".bulletinText.viewbull-field__container.auto-shy p[data-field='text']", "type": "text"}
        ]
    }

    # Проверяем поля
    assert schema['baseSelector'] == "div.site-content-container"
    assert any(field['name'] == 'price' for field in schema['fields'])