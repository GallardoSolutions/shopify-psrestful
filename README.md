# shopify-psrestful
CLI for Shopify &amp; PSRESTful integration - Updating PromoStandards Suppliers inventory &amp; Product import


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
```
 - run `export $(cat .env | xargs)`
 - run `./src/shopify_psrestful/cli.py -c add-ps-metafields` to see the available commands

### Development

- git clone git@github.com:GallardoSolutions/shopify-psrestful.git
- cd shopify-psrestful
- pyenv virtualenv 3.12.0 shopify-psrestful
- pyenv activate shopify-psrestful
- pip install poetry
- poetry install
