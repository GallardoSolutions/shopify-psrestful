import logging

from dataclasses import dataclass

import shopify

from shopify_psrestful.client import get_shopify_session

logger = logging.getLogger('shopify')


@dataclass
class Spec:
    name: str
    key: str
    description: str
    field_type: str = 'single_line_text_field'
    owner_type: str = 'PRODUCT'


SPECS = (
    # product
    Spec(name='Supplier Code', key='supplier_code', description='Supplier Code', field_type='single_line_text_field'),
    Spec(name='PS Product ID', key='product_id', description='Product ID from PromoStandards',
         field_type='single_line_text_field'),
    Spec(name='Extra ID', key='extra_id', description='Extra ID from PSRESTful API', field_type='number_integer'),
    Spec(name='Effective Date', key='effective_date',
         description='The Date this Product initially becomes available from the Supplier in ISO 8601 format',
         field_type='date'),
    Spec(name='Export', key='export', description='Product status for export', field_type='boolean'),
    Spec(name='Primary Material', key='primary_material', description='Primary material of construction',
         field_type='single_line_text_field'),
    Spec(name='Brand', key='brand', description='Brand of the Product', field_type='single_line_text_field'),
    Spec(name='Country of Origin', key='country_of_origin', description='Country of Origin of the Product',
         field_type='single_line_text_field'),
    Spec(name='Is Caution', key='is_caution',
         description='Cautionary status to review for specific warnings about using product data.',
         field_type='boolean'),
    Spec(name='Caution Comment', key='caution_comment', description='Caution', field_type='boolean'),
    Spec(name='Line Name', key='line_name', description='Line Name / Division to which this product belongs',
         field_type='single_line_text_field'),
    Spec(name='Minimum Quantity', key='minimum_quantity', description='Minimum quantity to order',
         field_type='number_integer'),
    Spec(name='Lead Time', key='lead_time', description='Lead time in days', field_type='number_integer'),
    Spec(name='Is On Demand', key='is_on_demand', description='Product is available on demand', field_type='boolean'),
    Spec(name='Is Rush Service', key='is_rush_service', description='Product is available as a rush service',
         field_type='boolean'),
    Spec(name='Imprint Size', key='imprint_size', description='The imprint Size', field_type='single_line_text_field'),
    Spec(name='Price Expires Date', key='price_expires_date', description='The Date this Product price expires',
         field_type='datetime'),
    Spec(name='Is Hazmat', key='is_hazmat', description='Contains hazardous material. A nil value indicates this it'
                                                        'is unknown or the data is not available by the supplier',
         field_type='boolean'),
    Spec(name='Price Expires Date', key='price_expires_date',
         description='The date that the pricing in the ProductPriceGroupArray portion of the response expires',
         field_type='datetime'),
    Spec(name='Default SetUp Charge', key='default_set_up_charge',
         description='The default setup charge for this product. Can be a textual description',
         field_type='single_line_text_field'),
    Spec(name='Default Run Charge', key='default_run_charge',
         description='The default RUN charge for this product. Can be a textual description',
         field_type='single_line_text_field'),
    Spec(name='UNSPSC Commodity Code', key='unspsc_commodity_code',
         description='The United Nations Standard Products and Services Code® (UNSPSC®) that best describes this '
                     'product. Note that the enumerated values are the UNSPSC "Commodity" codes. For more information, '
                     'refer to https://www.unspsc.org',
         field_type='number_integer'),
    # Variant
    Spec(name='Variant GTIN', key='variant_gtin', description='Global Trade Item Number',
         field_type='single_line_text_field'),
)


def create_meta_fields_from_specs(shopify_domain, access_token, meta_field_specs=SPECS):
    with get_shopify_session(shopify_domain, access_token):

        for spec in meta_field_specs:
            create_metafield(spec.name, spec.key, spec.description,
                             field_type=spec.field_type, owner_type=spec.owner_type)


def create_metafield(name: str, key: str, description: str,
                     namespace: str = 'psrestful',
                     field_type: str = 'single_line_text_field', owner_type: str = 'PRODUCT'):
    import pdb; pdb.set_trace()
    # https://shopify.dev/docs/apps/build/custom-data/metafields/list-of-data-types
    query = '''
    mutation CreateMetafieldDefinition($definition: MetafieldDefinitionInput!) {
      metafieldDefinitionCreate(definition: $definition) {
        createdDefinition {
          id
          name
          namespace
          key
          description
        }
        userErrors {
          field
          message
          code
        }
      }
    }
    '''
    variables = {
        "definition": {
            "name": name,
            "namespace": namespace,
            "key": key,
            "description": description,
            "type": field_type,
            "ownerType": owner_type
        }
    }

    response = shopify.GraphQL().execute(query, variables)
    return response
