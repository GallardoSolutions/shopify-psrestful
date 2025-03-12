import os
from contextlib import contextmanager

import shopify

from tenacity import retry, stop_after_attempt, wait_fixed

from . import settings


SHOPIFY_APP_PRIVATE_APP_PASSWORD = settings.SHOPIFY_APP_PRIVATE_APP_PASSWORD  # Admin API
SHOPIFY_APP_API_KEY = settings.SHOPIFY_APP_API_KEY
SHOPIFY_APP_API_SECRET = settings.SHOPIFY_APP_API_SECRET
SECRET_KEY = settings.SECRET_KEY
#
SHOPIFY_API_VERSION = settings.SHOPIFY_API_VERSION


@contextmanager
def get_shopify_session(shop_url: str, token: str = SHOPIFY_APP_PRIVATE_APP_PASSWORD):
    shopify.Session.setup(api_key=SHOPIFY_APP_API_KEY, secret=SECRET_KEY)

    session = shopify.Session(shop_url, SHOPIFY_API_VERSION, token)
    try:
        shopify.ShopifyResource.activate_session(session)
        yield session
    finally:
        shopify.ShopifyResource.clear_session()


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
