from tenacity import retry, stop_after_attempt, wait_fixed

import shopify


def get_all_shopify_products(limit=200):
    """
    Iterator to get all products from Shopify
    """
    get_next_page = True
    since_id = 0
    while get_next_page:
        products = get_shopify_products(since_id=since_id, limit=limit)

        for product in products:
            yield product
            since_id = product.id

        if len(products) < limit:
            get_next_page = False


@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def get_shopify_products(since_id=0, limit=100):
    # allows to retry when 429 error is raised
    return shopify.Product.find(since_id=since_id, limit=limit)
