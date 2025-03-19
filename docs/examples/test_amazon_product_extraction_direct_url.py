import asyncio
import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import io

# The code to test is assumed to be in the same file or imported; here, we include it for clarity
async def extract_amazon_products():
    browser_config = BrowserConfig(browser_type="chromium", headless=True)
    crawler_config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Product Details",
                "baseSelector": "div.site-content-container",
                "fields": [
                    {"name": "title", "selector": ".subject span[data-field='subject']", "type": "text"},
                    {"name": "id__num", "selector": ".viewbull-bulletin-id__num", "type": "text"},
                    {"name": "price", "selector": ".viewbull-summary-price__value", "type": "text"},
                    {"name": "availability", "selector": ".viewbull-field__container span[data-field='goodPresentState']", "type": "text"},
                    {"name": "condition", "selector": ".viewbull-field__container span[data-field='condition']", "type": "text"},
                    {"name": "manufacturer", "selector": ".viewbull-field__container span[data-field='manufacturer']", "type": "text"},
                    {"name": "part_number", "selector": ".viewbull-field__container span[data-field='autoPartsOemNumber']", "type": "text"},
                    {"name": "part_number_ZAMENA", "selector": "ul.oem-numbers__list[data-field='autoPartsSubstituteNumbers']", "type": "text"},
                    {"name": "compatibility", "selector": ".viewbull-field__container ul[data-field='autoPartsCompatibility'] li", "type": "text"},
                    {"name": "seller_name", "selector": ".seller-summary-user a", "type": "text"},
                    {"name": "image_urls", "selector": "div.image-gallery__big-image-container img", "type": "attribute", "attribute": "src", "multiple": True},
                    {"name": "image_descriptions", "selector": "div.image-gallery__big-image-container img", "type": "attribute", "attribute": "alt", "multiple": True},
                    {"name": "article_text", "selector": ".bulletinText.viewbull-field__container.auto-shy p[data-field='text']", "type": "text"}
                ]
            }
        )
    )
    url = "https://baza.drom.ru/novosibirsk/sell_spare_parts/bolt-mahovika-baw-bav-fenix-fenix-1044-evro-2-14mm-sht-495qa-05-010-g3616651496.html"
    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=crawler_config)
        if result and result.extracted_content:
            products = json.loads(result.extracted_content)
            for product in products:
                def print_product_details(data):
                    print("Информация о продукте:")
                    print(f"Заголовок: {data.get('title', 'Не найдено')}")
                    print(f"Идентификатор: {data.get('id__num', 'Не найдено')}")
                    print(f"Цена: {data.get('price', 'Не найдено')}")
                    print(f"Наличие: {data.get('availability', 'Не найдено')}")
                    print(f"Состояние: {data.get('condition', 'Не найдено')}")
                    print(f"Производитель: {data.get('manufacturer', 'Не найдено')}")
                    print(f"Номер детали: {data.get('part_number', 'Не найдено')}")
                    print(f"Номер детали (замена): {data.get('part_number_ZAMENA', 'Не найдено')}")
                    print(f"совместимость: {data.get('compatibility')}")
                    print(f"Имя продавца: {data.get('seller_name', 'Не найдено')}")
                    print("URL изображений:")
                    image_urls = data.get('image_urls', [])
                    if image_urls:
                        for url in image_urls:
                            print(f" - {url}")
                    else:
                        print(" - Не найдено")
                    print("Описания изображений:")
                    image_descriptions = data.get('image_descriptions', [])
                    if image_descriptions:
                        for desc in image_descriptions:
                            print(f" - {desc}")
                    else:
                        print(" - Не найдено")
                    print(f"Текст статьи: {data.get('article_text', 'Не найдено')}")
                print_product_details(product)

# Test class
class TestExtractAmazonProducts(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.loop = asyncio.get_event_loop()

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_successful_extraction(self, mock_crawler):
        """Test successful extraction with complete product data."""
        mock_result = MagicMock()
        mock_result.extracted_content = json.dumps([{
            "title": "Sample Product",
            "id__num": "98765",
            "price": "500 руб.",
            "availability": "В наличии",
            "condition": "Б/у",
            "manufacturer": "Sample Maker",
            "part_number": "XYZ789",
            "part_number_ZAMENA": "ABC123",
            "compatibility": ["Model X", "Model Y"],
            "seller_name": "Иван Петров",
            "image_urls": ["http://example.com/img1.jpg", "http://example.com/img2.jpg"],
            "image_descriptions": ["Image 1 desc", "Image 2 desc"],
            "article_text": "Sample article text."
        }])
        mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_result)

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            await extract_amazon_products()
            output = mock_stdout.getvalue()

        self.assertIn("Заголовок: Sample Product", output)
        self.assertIn("Идентификатор: 98765", output)
        self.assertIn("Цена: 500 руб.", output)
        self.assertIn("Наличие: В наличии", output)
        self.assertIn("Состояние: Б/у", output)
        self.assertIn("Производитель: Sample Maker", output)
        self.assertIn("Номер детали: XYZ789", output)
        self.assertIn("Номер детали (замена): ABC123", output)
        self.assertIn("совместимость: ['Model X', 'Model Y']", output)
        self.assertIn("Имя продавца: Иван Петров", output)
        self.assertIn(" - http://example.com/img1.jpg", output)
        self.assertIn(" - http://example.com/img2.jpg", output)
        self.assertIn(" - Image 1 desc", output)
        self.assertIn(" - Image 2 desc", output)
        self.assertIn("Текст статьи: Sample article text.", output)

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_no_extracted_content(self, mock_crawler):
        """Test behavior when no content is extracted."""
        mock_result = MagicMock()
        mock_result.extracted_content = None
        mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_result)

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            await extract_amazon_products()
            output = mock_stdout.getvalue()

        self.assertEqual(output.strip(), "")  # No output expected

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_missing_fields(self, mock_crawler):
        """Test handling of products with missing fields."""
        mock_result = MagicMock()
        mock_result.extracted_content = json.dumps([{
            "title": "Partial Product",
            "price": "300 руб."
        }])
        mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(return_value=mock_result)

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            await extract_amazon_products()
            output = mock_stdout.getvalue()

        self.assertIn("Заголовок: Partial Product", output)
        self.assertIn("Цена: 300 руб.", output)
        self.assertIn("Идентификатор: Не найдено", output)
        self.assertIn("Наличие: Не найдено", output)
        self.assertIn("Состояние: Не найдено", output)
        self.assertIn("Производитель: Не найдено", output)
        self.assertIn("Номер детали: Не найдено", output)
        self.assertIn("Номер детали (замена): Не найдено", output)
        self.assertIn("совместимость: None", output)
        self.assertIn("Имя продавца: Не найдено", output)
        self.assertIn("URL изображений:\n - Не найдено", output)
        self.assertIn("Описания изображений:\n - Не найдено", output)
        self.assertIn("Текст статьи: Не найдено", output)

    @patch('crawl4ai.AsyncWebCrawler')
    async def test_exception_handling(self, mock_crawler):
        """Test resilience to exceptions during crawling."""
        mock_crawler.return_value.__aenter__.return_value.arun = AsyncMock(side_effect=Exception("Network failure"))

        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            await extract_amazon_products()
            output = mock_stdout.getvalue()

        self.assertEqual(output.strip(), "")  # No output expected on failure

    def test_browser_config(self):
        """Test that browser configuration is set correctly."""
        config = BrowserConfig(browser_type="chromium", headless=True)
        self.assertEqual(config.browser_type, "chromium")
        self.assertTrue(config.headless)

if __name__ == "__main__":
    unittest.main()