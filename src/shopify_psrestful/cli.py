#!/usr/bin/env python
import argparse
from dotenv import load_dotenv

from shopify_psrestful.metafields import create_meta_fields_from_specs
from shopify_psrestful import settings


def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Shopify PSRESTful CLI")

    parser.add_argument("-c", "--cmd", type=str,
                        required=True, help="Commands available: add-ps-metafields, update-inventory")

    args = parser.parse_args()
    cms = args.cmd.lower()
    if args.cmd == 'add-ps-metafields':
        shopify_domain = settings.SHOPIFY_APP_SHOP_URL
        token = settings.SHOPIFY_APP_PRIVATE_APP_PASSWORD
        create_meta_fields_from_specs(shopify_domain, token)
        print("Metafields created successfully.")
    elif cms == 'update-inventory':
        #
        print("Updating inventory...")
    else:
        print("Unknown command.")


if __name__ == "__main__":
    main()
