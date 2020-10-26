#!/usr/bin/env python3

import json
import sys

import singer

from tap_starshipit.client import APIClient
from tap_starshipit.discover import discover
from tap_starshipit.sync import sync

LOGGER = singer.get_logger()

REQUIRED_CONFIG_KEYS = [
    'start_date',
    'subscription_key',
    'api_key'
]

def do_discover(client):
    LOGGER.info('Testing authentication')
    try:
        # test by making the client fetch any order
        client.get(
            '/orders?order_number=ZZZZ',
            endpoint='____')
    except:
        raise Exception('Error testing to StarShipIt authentication')

    LOGGER.info('Starting discover')
    catalog = discover(client)
    json.dump(catalog.to_dict(), sys.stdout, indent=2)
    LOGGER.info('Finished discover')

@singer.utils.handle_top_exception(LOGGER)
def main():
    parsed_args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    with APIClient(parsed_args.config, parsed_args.config_path) as client:
        if parsed_args.discover:
            do_discover(client)
        else:
            sync(client,
                 parsed_args.catalog,
                 parsed_args.state,
                 parsed_args.config['start_date'])


if __name__ == "__main__":
    main()
