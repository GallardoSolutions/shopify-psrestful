import logging


import shopify
from tenacity import retry, stop_after_attempt, wait_fixed


from .client import get_shopify_session
from .products import get_all_shopify_products
from .metafields import get_supplier_and_product_id
from .ps_client import PSClient
from .domain import InventoryLevelsResponse


from . import settings

logger = logging.getLogger('shopify')


class InventoryService:

    def __init__(self):
        self.client = PSClient()

    def update_inventory(self, shopify_domain: str = settings.SHOPIFY_APP_SHOP_URL,
                         token: str = settings.SHOPIFY_APP_PRIVATE_APP_PASSWORD):
        with get_shopify_session(shopify_domain, token):
            location_id = self.get_default_location_id()
            self._update_inventory(location_id)
            logger.info('Inventory update complete')

    @staticmethod
    def get_default_location_id():
        locations = shopify.Location.find()
        return locations[0].id

    def _update_inventory(self, location_id):
        for ix, product in enumerate(get_all_shopify_products()):
            logger.info(f'Processing product {ix} - {product.title}')
            supplier_code, product_id = get_supplier_and_product_id(product)
            if not supplier_code or not product_id:
                logger.error(f'Product {product.title} has no supplier code or product id')
                continue
            try:
                inv_resp = self.client.get_inventory(supplier_code, product_id)
                if inv_resp.is_ok:
                    for variant in product.variants:
                        self.update_variant_inventory(inv_resp, location_id, variant)
            except Exception as e:  # noqa
                logger.error(f'Error processing product {product.title}: {e}')
                continue

    @staticmethod
    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def update_variant_inventory(inv_resp: InventoryLevelsResponse, location_id, variant):
        part_id = variant.attributes['sku']
        available_inventory = inv_resp.get_available_inventory(part_id)
        available_inventory = int(available_inventory) if available_inventory else 0
        logger.info(f'Processing variant {part_id} -> {available_inventory}')
        inventory_item_id = variant.inventory_item_id
        inventory_level = shopify.InventoryLevel.set(location_id=location_id,
                                                     inventory_item_id=inventory_item_id,
                                                     available=available_inventory)
        logger.info(f"Updated inventory level: {inventory_level}")
