from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json
from playwright.async_api import Page, BrowserContext
#todo deep не вводит результаты поиска и показывает сразу все - это надо исправить.
async def extract_drom_products():

    # Конфигурация прокси
    proxy_config = {
        "server": "la.residential.rayobyte.com:8000",
        "username": "1_tcrossa_ru-dc",
        "password": "iTjnzJt7divd4VA4sQYxwWOcBCMc"
    }


    # Initialize browser config
    browser_config = BrowserConfig(
        headless=False,
        proxy_config=proxy_config
    )

    # Initialize crawler config with JSON CSS extraction strategy
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Drom Product Search Results",
                "baseSelector": ".bull-item",  # Базовый селектор для карточки товара
                "fields": [
                    {
                        "name": "title",
                        "selector": ".bull-item__self-link",  # Селектор для заголовка
                        "type": "text",
                    },
                    {
                        "name": "price",
                        "selector": ".price-block__price",  # Селектор для цены
                        "type": "text",
                    },
                    {
                        "name": "url",
                        "selector": ".bull-item__self-link",  # Селектор для ссылки на товар
                        "type": "attribute",
                        "attribute": "href",
                    },
                    {
                        "name": "image",
                        "selector": ".bull-image-container img",  # Селектор для изображения товара
                        "type": "attribute",
                        "attribute": "src",
                    },
                    {
                        "name": "delivery_info",
                        "selector": ".bull-delivery",  # Селектор для информации о доставке
                        "type": "text",
                        "multiple": True,
                    },
                    {
                        "name": "seller",
                        "selector": ".ellipsis-text__left-side",  # Селектор для продавца
                        "type": "text",
                    },
                ],
            }))

    url = "https://baza.drom.ru/sell_spare_parts/model/shaanxi/"

    async def after_goto(
        page: Page, context: BrowserContext, url: str, response: dict, **kwargs
    ):
        """Hook called after navigating to each URL"""
        print(f"[HOOK] after_goto - Successfully loaded: {url}")

        try:
            # Wait for search results to load
            await page.wait_for_selector('.bull-item', timeout=10000)
            print("[HOOK] Search results loaded!")

        except Exception as e:
            print(f"[HOOK] Error during search operation: {str(e)}")

        return page

    # Use context manager for proper resource handling
    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawler.crawler_strategy.set_hook("after_goto", after_goto)

        # Extract the data
        result = await crawler.arun(url=url, config=crawler_config)

        # Process and print the results
        if result and result.extracted_content:
            # Parse the JSON string into a list of products
            products = json.loads(result.extracted_content)

            # Process each product in the list
            for product in products:
                print("\nProduct Details:")
                print(f"Title: {product.get('title')}")
                print(f"Price: {product.get('price')}")
                print(f"URL: {product.get('url')}")
                if product.get("delivery_info"):
                    print(f"Delivery: {' '.join(product['delivery_info'])}")
                print(f"Seller: {product.get('seller')}")
                print("-" * 80)


if __name__ == "__main__":
    import asyncio

    asyncio.run(extract_drom_products())