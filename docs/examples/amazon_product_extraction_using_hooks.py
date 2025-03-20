from crawl4ai import AsyncWebCrawler, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from crawl4ai.async_configs import BrowserConfig, CrawlerRunConfig
import json
from playwright.async_api import Page, BrowserContext

#todo предусмотреть вывод всех стро а не только 10 GROK

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

    # Конфигурация краулера с новой схемой
    crawler_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        extraction_strategy=JsonCssExtractionStrategy(
            schema={
                "name": "Drom Product Details",
                "baseSelector": ".bullViewEx",
                "fields": [
                    {"name": "bulletin_id", "selector": ".viewbull-bulletin-id__num", "type": "text"},
                    {"name": "title", "selector": "h1.subject span.inplace", "type": "text"},
                    {"name": "price", "selector": ".viewbull-summary-price__value", "type": "text"},
                    {"name": "image", "selector": ".image-gallery__big-image", "type": "attribute", "attribute": "src"},
                    {"name": "seller", "selector": ".seller-summary-user .userNick a", "type": "text"},
                    {"name": "seller_rating", "selector": ".userRating a.ratingPositive", "type": "text"},
                    {"name": "reviews_count", "selector": ".separated-list__item a[href*='feedbacks']", "type": "text"},
                    {"name": "availability", "selector": ".field[data-field='goodPresentState'] .inplace", "type": "text"},
                    {"name": "condition", "selector": ".field[data-field='condition'] .inplace", "type": "text"},
                    {"name": "manufacturer", "selector": ".field[data-field='manufacturer'] .inplace", "type": "text"},
                    {"name": "compatibility", "selector": ".field.autoPartsModel ul.inplace li", "type": "text", "multiple": True},
                    {"name": "description", "selector": ".bulletinText p.inplace", "type": "text"},
                    {"name": "delivery_info", "selector": ".field[data-field='delivery-pickupAddress-delivery.comment'] .inplace", "type": "text"},
                ],
            }
        )
    )

    url = "https://baza.drom.ru/sell_spare_parts/model/shaanxi/"

    async def after_goto(page: Page, context: BrowserContext, url: str, response: dict, **kwargs):
        """Хук после перехода на страницу"""
        print(f"[HOOK] after_goto - Successfully loaded: {url}")

        try:
            # Ожидание поля ввода поиска
            search_box = await page.wait_for_selector("input[name='query']", timeout=5000)
            await search_box.fill("Кабина Shaanxi")

            # Нажатие Enter для выполнения поиска
            await page.press("input[name='query']", "Enter")
            await page.wait_for_selector(".bull-item__self-link", timeout=10000)
            print("[HOOK] Search completed and results loaded!")

            # Переход на первый товар
            first_product_link = await page.wait_for_selector(".bull-item__self-link", timeout=5000)
            product_url = await first_product_link.get_attribute("href")
            await page.goto(f"https://baza.drom.ru{product_url}")
            await page.wait_for_selector(".bullViewEx", timeout=10000)
            print(f"[HOOK] Navigated to product page: {product_url}")

        except Exception as e:
            print(f"[HOOK] Error during operation: {str(e)}")

        return page

    # Запуск краулера
    async with AsyncWebCrawler(config=browser_config) as crawler:
        crawler.crawler_strategy.set_hook("after_goto", after_goto)
        result = await crawler.arun(url=url, config=crawler_config)

        # Обработка результатов
        if result and result.extracted_content:
            product = json.loads(result.extracted_content)[0]  # Берем первый элемент, так как парсим одну страницу товара
            print("\nProduct Details:")
            print(f"Bulletin ID: {product.get('bulletin_id')}")
            print(f"Title: {product.get('title')}")
            print(f"Price: {product.get('price')}")
            print(f"Image: {product.get('image')}")
            print(f"Seller: {product.get('seller')}")
            print(f"Seller Rating: {product.get('seller_rating')}")
            print(f"Reviews: {product.get('reviews_count')}")
            print(f"Availability: {product.get('availability')}")
            print(f"Condition: {product.get('condition')}")
            print(f"Manufacturer: {product.get('manufacturer')}")
            if product.get("compatibility"):
                print(f"Compatibility: {', '.join(product['compatibility'])}")
            print(f"Description: {product.get('description')}")
            print(f"Delivery Info: {product.get('delivery_info')}")
            print("-" * 80)

if __name__ == "__main__":
    import asyncio
    asyncio.run(extract_drom_products())