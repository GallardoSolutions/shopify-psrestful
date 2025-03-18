from dataclasses import dataclass

from psdomain.model.base import StrEnum
from psdomain.model.product_data.v_1_0_0 import ProductResponseV100
from psdomain.model.product_data.v_2_0_0 import ProductResponseV200
from psdomain.model.inventory.v_2_0_0 import InventoryLevelsResponseV200
from psdomain.model.inventory.v_1_2_1 import InventoryLevelsResponseV121

ORDERED_SERVICES = ['Product', 'MED', 'PPC', 'INV', 'PO', 'ODRSTAT', 'OSN', 'INVC']


class ServiceCode(StrEnum):
    INV = 'Inventory'
    PPC = 'Price and Configuration'  # Product Price and Configuration
    Product = 'Product Data'
    INVC = 'Invoice'
    ODRSTAT = 'Order Status'
    OSN = 'Order Shipment Notification'
    MED = 'Media Content'
    PO = 'Purchase Order'
    PDC = 'Product Compliance'
    SPCC = 'Supplier Price and Configuration'

    def __str__(self):
        return self.name


class ServiceVersion(StrEnum):
    V_1_0_0 = 'v1.0.0'
    V_1_1_0 = 'v1.1.0'
    V_1_2_1 = 'v1.2.1'
    V_2_0_0 = 'v2.0.0'

    @classmethod
    def fromstr(cls, version: str) -> 'ServiceVersion':
        return cls('v' + version) if version else None


class Environment(StrEnum):
    PROD = 'PROD'
    STAGING = 'STAGING'


class Currency(StrEnum):
    # for now only these two currencies are supported
    USD = 'USD'
    CAD = 'CAD'


class Function(StrEnum):
    # Product Data
    GetSellables = 'getSellables',
    GetProduct = 'getProduct'
    GetProductCloseout = 'getProductCloseout'
    GetProductDateModified = 'getProductDateModified'
    # Media Content
    GetMediaContent = 'getMediaContent'
    GetMediaDateModified = 'getMediaDateModified'
    # Product Pricing and Configuration
    GetAvailableLocations = 'getAvailableLocations'
    GetDecorationColors = 'getDecorationColors'
    GetFobPoints = 'getFobPoints'
    GetAvailableCharges = 'getAvailableCharges'
    GetConfigurationAndPricing = 'getConfigurationAndPricing'
    # Inventory
    GetFilterValues = 'getFilterValues'
    GetInventoryLevels = 'getInventoryLevels'
    # Purchase Order
    GetSupportedOrderTypes = 'getSupportedOrderTypes'
    SendPO = 'sendPO'
    # Order Status
    GetOrderStatusTypes = 'getOrderStatusTypes'
    GetOrderStatusDetails = 'getOrderStatusDetails'
    GetOrderStatus = 'getOrderStatus'
    GetServiceMethods = 'getServiceMethods'
    GetIssue = 'getIssue'
    # OSN
    GetOrderShipmentNotification = 'getOrderShipmentNotification'
    # Invoice
    GetInvoices = 'getInvoices'
    GetVoidedInvoices = 'getVoidedInvoices'


@dataclass
class APIParams:
    environment: Environment
    supplier_code: str
    service: ServiceCode
    version: ServiceVersion
    function: Function
    query_params: dict = None
    body_params: dict = None
    headers: dict = None
    product_ids_only: bool = False


ProductResponse = ProductResponseV100 | ProductResponseV200
InventoryLevelsResponse = InventoryLevelsResponseV121 | InventoryLevelsResponseV200


def get_product_class(version: ServiceVersion):
    product_classes = {'v1.0.0': ProductResponseV100, 'v2.0.0': ProductResponseV200}
    return product_classes[version.value]


def get_inventory_class(version: ServiceVersion):
    inventory_classes = {'v1.2.1': InventoryLevelsResponseV121, 'v2.0.0': InventoryLevelsResponseV200}
    return inventory_classes[version.value]
