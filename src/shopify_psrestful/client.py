from contextlib import contextmanager

import shopify

from . import settings


SHOPIFY_APP_PRIVATE_APP_PASSWORD = settings.SHOPIFY_APP_PRIVATE_APP_PASSWORD  # Admin API
SHOPIFY_APP_API_KEY = settings.SHOPIFY_APP_API_KEY
SHOPIFY_APP_API_SECRET = settings.SHOPIFY_APP_API_SECRET
#
SHOPIFY_API_VERSION = settings.SHOPIFY_API_VERSION


@contextmanager
def get_shopify_session(shop_url: str, token: str = SHOPIFY_APP_PRIVATE_APP_PASSWORD):
    shopify.Session.setup(api_key=SHOPIFY_APP_API_KEY, secret=SHOPIFY_APP_API_SECRET)

    session = shopify.Session(shop_url, SHOPIFY_API_VERSION, token)
    try:
        shopify.ShopifyResource.activate_session(session)
        yield session
    finally:
        shopify.ShopifyResource.clear_session()
