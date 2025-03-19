"""
This example demonstrates how to use JSON CSS extraction to scrape product information 
from Amazon search results. It shows how to extract structured data like product titles,
prices, ratings, and other details using CSS selectors.
"""

from crawl4ai import AsyncWebCrawler
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json


async def extract_amazon_products():
    # Initialize browser config
    browser_config = BrowserConfig(browser_type="chromium", headless=True)

    # Initialize crawler config with JSON CSS extraction strategy
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


    # Example search URL (you should replace with your actual Amazon URL)
    url = "https://baza.drom.ru/novosibirsk/sell_spare_parts/bolt-mahovika-baw-bav-fenix-fenix-1044-evro-2-14mm-sht-495qa-05-010-g3616651496.html"

    # Use context manager for proper resource handling
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Extract the data
        result = await crawler.arun(url=url, config=crawler_config)

        # Process and print the results
        if result and result.extracted_content:
            # Parse the JSON string into a list of products
            products = json.loads(result.extracted_content)

            # После получения результата парсинга (result.extracted_content)
            if result and result.extracted_content:
                products = json.loads(result.extracted_content)

                for product in products:
                    def print_product_details(data):
                        """Выводит информацию о продукте на экран в читаемом формате."""
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


if __name__ == "__main__":
    import asyncio

    asyncio.run(extract_amazon_products())
