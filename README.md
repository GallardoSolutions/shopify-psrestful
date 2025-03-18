# shopify-psrestful

CLI for Shopify &amp; PSRESTful integration - Updating PromoStandards Suppliers inventory &amp; Product import.
This is a CLI tool to help with the integration of Shopify and [PSRESTful](https://psrestful.com/), and it is meant to
be used as a standalone tool but in combination with the CSV Exporter
in [PSRESTful](https://psrestful.com/csv-generator-explained/).

It will allow you to add `metafields` to Shopify products so the CSV Exporter will fill out more information.
Besides that, it will allow you to update inventory levels in Shopify based on the data
from [PSRESTful](https://psrestful.com/).
If you already have products in your store and want to update the inventory, you just need to add the metafields
`supplier_code` and `product_id` to your products. Then, you will be ready to update inventory using this script.

The list of available suppliers in [PSRESTful](https://psrestful.com/) is available
at [integrated suppliers](https://psrestful.com/integrated-suppliers/?configured=yes).

## Installation

- git clone git@github.com:GallardoSolutions/shopify-psrestful.git
- cd shopify-psrestful
- cd shopify-psrestful
- pyenv virtualenv 3.12.0 shopify-psrestful
- pyenv activate shopify-psrestful
- pip install poetry
- poetry install

## Requirements

- tenacity
- requests

## Usage

- Add a `.env` file with the following variables and fill out the values:

```bash
SHOPIFY_APP_API_KEY=
SHOPIFY_APP_API_SECRET=
SHOPIFY_APP_SHOP_URL=
SHOPIFY_APP_API_VERSION='2024-07'
SHOPIFY_APP_PRIVATE_APP_PASSWORD=  # Admin API
PS_RESTFUL_API_KEY=
PS_REST_API=https://api.psrestful.com/
```

- run `export $(cat .env | xargs)`
- run `./src/shopify_psrestful/cli.py -c add-ps-metafields` to add the metafields to Shopify
- run `./src/shopify_psrestful/cli.py -c update-inventory` to update the inventory in Shopify

If running on a Linux box via ssh, you could use nohup to run the script in the background:

```bash
nohup ./src/shopify_psrestful/cli.py -c update-inventory &
```

### Development

- git clone git@github.com:GallardoSolutions/shopify-psrestful.git
- cd shopify-psrestful
- pyenv virtualenv 3.12.0 shopify-psrestful
- pyenv activate shopify-psrestful
- pip install poetry
- poetry install
