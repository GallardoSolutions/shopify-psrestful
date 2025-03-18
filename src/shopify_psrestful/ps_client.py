import logging

import time
from decimal import Decimal

from tenacity import retry, stop_after_attempt, wait_fixed

import httpx

from . import settings

from .domain import APIParams, ServiceVersion, ServiceCode, Environment, Function, ProductResponse, \
    get_product_class, InventoryLevelsResponse, get_inventory_class
from .ps_services import ServiceHelper

PS_RESTFUL_API_KEY = settings.PS_RESTFUL_API_KEY
PS_REST_API = settings.PS_REST_API

TWO_PLACES = Decimal(10) ** -2

logger = logging.getLogger('ps')


class PSClient:
    def __init__(self):
        self.headers = {
            'x-api-key': PS_RESTFUL_API_KEY,
            "accept": "application/json"
        }
        self.api = APIHelper(sync=True)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def get_product(self, supplier_code: str, product_id: str) -> ProductResponse:
        response, _, version = self.api.get_product_detail(supplier_code, environment=Environment.PROD,
                                                           headers=self.headers,
                                                           product_id=product_id)
        if response.status_code == 429:  # rate limit
            logger.warning(f'{supplier_code} - Rate limit reached while getting product {product_id}')
            raise Exception(f'{supplier_code} - Rate limit reached')
        if response.status_code != 200:
            logger.error(f'Error getting product {product_id} for supplier {supplier_code}: {response.text}')
            raise Exception(f'Error getting product {product_id} for supplier {supplier_code}: {response.text}')
        return self.api.gen_product_response(response, ServiceVersion.fromstr(version))

    def get_products(self, supplier_code: str, category: str, product_ids: list[str], max_products: int = 200):
        category, sub_category = self.gen_categories(category)
        resp = self.get_sellable_product_ids(supplier_code)
        all_products = resp['products']
        if product_ids:
            all_products = [p for p in all_products if p in product_ids]
        logger.info(f'max_products: {max_products}')
        for ix, product_id in enumerate(all_products):
            product_str = f'{supplier_code}-{product_id}'
            try:
                logger.info(f'Getting product {ix + 1} of {len(all_products)} => {product_str}')
                if ix >= max_products:
                    break
                product = self.get_product(supplier_code, product_id)
                if product and product.data:
                    if category:
                        if product.belongs_to(category, sub_category):
                            yield product
                    else:
                        yield product
                else:
                    logger.warning(f'Product {product_str} not found -> {product.message}')
            except Exception as e:
                logger.error(f'Error getting product {product_str}: {e}')

    def get_sellable_product_ids(self, supplier_code):
        response, _, _ = self.api.get_sellable_product_ids(supplier_code, headers=self.headers,
                                                           environment=Environment.PROD)
        return response.json()

    def get_inventory(self, supplier_code: str, product_id: str) -> InventoryLevelsResponse:
        response, _, version = self.api.get_inventory(supplier_code, environment=Environment.PROD,
                                                      headers=self.headers, product_id=product_id)
        if response.status_code == 429:
            msg = f'{supplier_code} - Rate limit reached while getting inventory for product {product_id}'
            logger.warning(msg)
            raise Exception(msg)
        if response.status_code != 200:
            msg = f'Error getting inventory for {product_id} for supplier {supplier_code}: {response.text}'
            logger.error(msg)
            raise Exception(msg)
        return self.api.gen_inventory_response(response, version)

    @staticmethod
    def gen_categories(category: str | None) -> tuple[str, str | None]:
        sub_category = None
        if category:
            category = category.lower()
            if '>' in category:
                lst = category.split('>')
                category = lst[0].strip()
                sub_category = lst[1].strip()
        return category, sub_category


class APIHelper:
    def __init__(self, sync: bool = True):
        timeout = 3000
        self.client = httpx.Client(timeout=timeout) if sync else httpx.AsyncClient(timeout=timeout)
        self.service_helper = ServiceHelper()

    def perform_request(self, params: APIParams, product_id: str = None):
        url = self.gen_url(params, product_id)
        qry_params = self.gen_qry_params(params)
        env = params.environment
        qry_params['environment'] = env if isinstance(env, str) else env.value
        #
        ts = time.monotonic()
        result = self.client.get(url, params=qry_params, headers=params.headers)
        te = time.monotonic()
        return result, self.get_duration(te - ts)

    async def a_perform_request(self, params: APIParams, product_id: str = None):
        url = self.gen_url(params, product_id)
        qry_params = self.gen_qry_params(params)
        env = params.environment
        qry_params['environment'] = env if isinstance(env, str) else env.value

        ts = time.monotonic()
        result = await self.client.get(url, params=qry_params, headers=params.headers)
        te = time.monotonic()
        return result, self.get_duration(te - ts)

    def gen_qry_params(self, params: APIParams):
        ret = params.query_params or {}
        new_ret = {k: v for k, v in ret.items() if v}
        return new_ret

    def gen_url(self, params: APIParams, product_id):
        serv_func = self.gen_srv_func(params.service, params.function, params.product_ids_only)
        url = f'{PS_REST_API}{params.version.value}/suppliers/{params.supplier_code}/{serv_func}'
        if product_id:
            url += f'/{product_id}'
        return url

    @staticmethod
    def gen_srv_func(service: ServiceCode, func: Function, product_ids_only: bool = False) -> str:
        service = service.name.lower()
        func = func.lower()
        trans = {
            # Product Data
            'product - getsellables': 'sellables',
            'product - getproduct': 'products',
            'product - getproductcloseout': 'products-closeout',
            'product - getproductdatemodified': 'products-modified-since',
            # Media Content
            'med - getmediacontent': 'medias',
            'med - getmediadatemodified': 'media-modified-since',
            # Product Pricing and Configuration
            'ppc - getavailablelocations': 'available-locations',
            'ppc - getdecorationcolors': 'decoration-colors',
            'ppc - getfobpoints': 'fob-points',
            'ppc - getavailablecharges': 'available-charges',
            'ppc - getconfigurationandpricing': 'pricing-and-configuration',
            # Inventory
            'inv - getfiltervalues': 'inventory/filter-values',
            'inv - getinventorylevels': 'inventory',
            # Purchase Order
            'po - getsupportedordertypes': 'supported-order-types',
            'po - sendpo': 'purchase-orders',
            # Order Status
            'odrstat - getorderstatustypes': 'order-status-types',
            'odrstat - getorderstatusdetails': 'order-status-details',
            'odrstat - getorderstatus': 'order-status',
            'odrstat - getServiceMethods': 'service-methods',
            'odrstat - getIssue': 'issues',
            # OSN
            'osn - getordershipmentnotification': 'order-shipment-notifications',
            # Invoice
            'invc - getinvoices': 'invoices',
            'invc -  getvoidedinvoices': 'voided-invoices',

        }
        ret = trans.get(f'{service} - {func}')
        if ret is None:
            raise ValueError(f'Invalid service/function combination: {service}/{func}')
        if product_ids_only:
            ret = ret.replace('sellables', 'sellable-product-ids')
        return ret

    def get_sellables(self, supplier_code: str,
                      version: ServiceVersion = None,
                      headers: dict = None,
                      environment: Environment = Environment.PROD):
        version = self.get_latest_product_data_version(supplier_code, version)
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetSellables)
        result, duration = self.perform_request(params)
        return result, duration, version

    async def a_get_sellables(self, supplier_code: str,
                              version: ServiceVersion = None,
                              headers: dict = None,
                              environment: Environment = Environment.PROD):
        version = self.get_latest_product_data_version(supplier_code, version)
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetSellables)
        result, duration = await self.a_perform_request(params)
        return result, duration, version

    def get_sellable_product_ids(self, supplier_code: str,
                                 version: ServiceVersion = None,
                                 headers: dict = None,
                                 environment: Environment = Environment.PROD):
        version = self.get_latest_product_data_version(supplier_code, version)
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetSellables, product_ids_only=True)
        result, duration = self.perform_request(params)
        return result, duration, version

    async def a_get_sellable_product_ids(self, supplier_code: str,
                                         version: ServiceVersion = None,
                                         headers: dict = None,
                                         environment: Environment = Environment.PROD):
        version = self.get_latest_product_data_version(supplier_code, version)
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetSellables, product_ids_only=True)
        result, duration = await self.a_perform_request(params)
        return result, duration, version

    @staticmethod
    def gen_sellables_resp(response):
        if response.status_code == 200:
            resp = response.json()
            error = resp.get('ServiceMessageArray') or resp.get('ErrorMessage')
            if error:
                raise Exception(error)
            else:
                product_sellable = []
                if 'ProductSellableArray' in resp and resp['ProductSellableArray']:
                    product_sellable = resp['ProductSellableArray']['ProductSellable']
                return product_sellable
        return []

    def get_latest_product_data_version(self, supplier_code, version=None) -> ServiceVersion:
        if version is None:
            api_version = self.service_helper.get_latest_code(supplier_code, 'Product')
            version = ServiceVersion('v' + api_version) if api_version else None
        if version is None:
            raise ValueError(f'No product version found for supplier {supplier_code}')
        return version

    def get_latest_inventory_version(self, supplier_code, version) -> ServiceVersion | None:
        if version is None:
            api_version = self.service_helper.get_latest_code(supplier_code, 'INV')
            version = ServiceVersion('v' + api_version) if api_version else None
        if version is None:
            raise ValueError(f'No inventory version found for supplier {supplier_code}')
        return version

    def get_product_detail(self, supplier_code: str, environment: Environment, headers: dict,
                           product_id: str, version: ServiceVersion = None):
        version = self.get_latest_product_data_version(supplier_code, version)
        if version is None:
            raise ValueError(f'No pro version found for supplier {supplier_code}')
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetProduct)
        resp, duration = self.perform_request(params, product_id=product_id)
        return resp, duration, version

    async def a_get_product_detail(self, supplier_code: str, environment: Environment, headers: dict,
                                   product_id: str, version: ServiceVersion = None):
        version = self.get_latest_product_data_version(supplier_code, version)
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.Product, function=Function.GetProduct)
        return await self.a_perform_request(params, product_id=product_id)

    def get_inventory(self, supplier_code: str, environment: Environment, headers: dict,
                      product_id: str, version: ServiceVersion = None, filter_type=None, filter_value=None):
        params, version = self._get_inventory_common(environment, supplier_code, version,
                                                     filter_type, filter_value, headers)
        resp, duration = self.perform_request(params, product_id=product_id)
        return resp, duration, version

    async def a_get_inventory(self, supplier_code: str, environment: Environment, headers: dict,
                              product_id: str, version: ServiceVersion = None, filter_type=None, filter_value=None):
        params, version = self._get_inventory_common(environment, supplier_code, version,
                                                     filter_type, filter_value, headers)
        resp, duration = self.a_perform_request(params, product_id=product_id)
        return resp, duration, version

    def _get_inventory_common(self, environment, supplier_code, version, filter_type, filter_value, headers):
        version = self.get_latest_inventory_version(supplier_code, version)
        if version is None:
            raise ValueError(f'No inventory version found for supplier {supplier_code}')
        params = APIParams(supplier_code=supplier_code, version=version, headers=headers, environment=environment,
                           service=ServiceCode.INV, function=Function.GetInventoryLevels)
        if filter_type and filter_value:
            params.query_params = {filter_type: filter_value}
        return params, version

    @staticmethod
    def get_duration(duration: float) -> Decimal:
        return Decimal(duration * 1000).quantize(TWO_PLACES)

    @staticmethod
    def gen_product_response(response, version: ServiceVersion) -> ProductResponse:
        cls = get_product_class(version)
        return cls.model_validate_json(response.content)

    @staticmethod
    def gen_inventory_response(response, version: ServiceVersion) -> InventoryLevelsResponse:
        cls = get_inventory_class(version)
        if response.status_code == 200:
            return cls.model_validate_json(response.content)
        logger.error(f'Failed to get inventory response for supplier code {response.request.method} ')
        raise Exception(response.content)
