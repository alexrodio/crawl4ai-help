"""
This example demonstrates how to use JSON CSS extraction to scrape product information 
from Amazon search results. It shows how to extract structured data like product titles,
prices, ratings, and other details using CSS selectors.
"""

from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json
from playwright.async_api import Page, BrowserContext


async def extract_amazon_products():
    # Initialize browser config
    browser_config = BrowserConfig(
        # browser_type="chromium",
        headless=False
    )

    # Initialize crawler config with JSON CSS extraction strategy nav-search-submit-button
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Amazon Product Search Results",
                "baseSelector": "[data-component-type='s-search-result']",  # Базовый селектор для карточки товара
                "fields": [
                    {
                        "name": "asin",
                        "selector": "",
                        "type": "attribute",
                        "attribute": "data-asin",  # ASIN обычно хранится в атрибуте data-asin
                    },
                    {
                        "name": "title",
                        "selector": "h2.a-size-medium.a-color-base.a-text-normal",  # Селектор для заголовка
                        "type": "text",
                    },
                    {
                        "name": "url",
                        "selector": "h2 a.a-link-normal",  # Селектор для ссылки на товар
                        "type": "attribute",
                        "attribute": "href",
                    },
                    {
                        "name": "image",
                        "selector": ".s-image",  # Селектор для изображения товара
                        "type": "attribute",
                        "attribute": "src",
                    },
                    {
                        "name": "rating",
                        "selector": ".a-icon-star-small .a-icon-alt",  # Селектор для рейтинга
                        "type": "text",
                    },
                    {
                        "name": "reviews_count",
                        "selector": ".a-size-small.s-underline-text",  # Селектор для количества отзывов
                        "type": "text",
                    },
                    {
                        "name": "price",
                        "selector": ".a-price .a-offscreen",  # Селектор для текущей цены
                        "type": "text",
                    },
                    {
                        "name": "original_price",
                        "selector": ".a-price.a-text-price .a-offscreen",
                        # Селектор для оригинальной цены (если есть скидка)
                        "type": "text",
                    },
                    {
                        "name": "sponsored",
                        "selector": ".puis-sponsored-label-text",  # Селектор для спонсируемых товаров
                        "type": "exists",
                    },
                    {
                        "name": "delivery_info",
                        "selector": "[data-cy='delivery-recipe'] .a-color-base",  # Селектор для информации о доставке
                        "type": "text",
                        "multiple": True,
                    },
                ],
            }))

    url = "https://www.amazon.com/"

    async def after_goto(
        page: Page, context: BrowserContext, url: str, response: dict, **kwargs
    ):
        """Hook called after navigating to each URL"""
        print(f"[HOOK] after_goto - Successfully loaded: {url}")

        try:
            # Wait for search box to be available
            search_box = await page.wait_for_selector(
                "#twotabsearchtextbox", timeout=1000
            )

            # Type the search query
            await search_box.fill("Samsung Galaxy Tab")

            # Get the search button and prepare for navigation
            search_button = await page.wait_for_selector(
                "#nav-search-submit-button", timeout=1000
            )

            # Click with navigation waiting
            await search_button.click()

            # Wait for search results to load
            await page.wait_for_selector(
                '[data-component-type="s-search-result"]', timeout=10000
            )
            print("[HOOK] Search completed and results loaded!")

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
                print(f"ASIN: {product.get('asin')}")
                print(f"Title: {product.get('title')}")
                print(f"Price: {product.get('price')}")
                print(f"Original Price: {product.get('original_price')}")
                print(f"Rating: {product.get('rating')}")
                print(f"Reviews: {product.get('reviews_count')}")
                print(f"Sponsored: {'Yes' if product.get('sponsored') else 'No'}")
                if product.get("delivery_info"):
                    print(f"Delivery: {' '.join(product['delivery_info'])}")
                print("-" * 80)


if __name__ == "__main__":
    import asyncio

    asyncio.run(extract_amazon_products())
