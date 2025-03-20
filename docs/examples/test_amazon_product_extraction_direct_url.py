import json

    schema = {
        "name": "Product Details",
        "baseSelector": "div.site-content-container",
        "fields": [
            {"name": "title", "selector": ".subject span[data-field='subject']", "type": "text"},
            {"name": "id__num", "selector": ".viewbull-bulletin-id__num", "type": "text"},
            {"name": "price", "selector": ".viewbull-summary-price__value", "type": "text"},
            {"name": "seller_name", "selector": ".seller-summary-user a", "type": "text"},
        ]
    }
