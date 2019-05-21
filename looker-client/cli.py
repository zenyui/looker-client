#!/usr/bin/env python

import logging
import argparse
import dotenv
import signal
import sys
import client
from client.workflows import registry

def main():
    p = argparse.ArgumentParser('api client')
    p.add_argument('-v', dest='verbose', help='verbose logging', action='store_true')
    p.add_argument('--env', dest='env', help='env file', default='credentials.env')
    p.add_argument('--log', dest='log', help='optional log filepath')
    s = p.add_subparsers(dest='which')

    handlers = {}

    for workflow in registry:
        workflow.register(s, handlers)

    args = p.parse_args()

    if not args.which:
        p.print_help()
        exit()

    dotenv.load_dotenv(args.env)

    handler = handlers.get(args.which)
    assert handler, 'not found: {}'.format(args.which)

    client.helpers.configure_logging(args.verbose, args.log)
    logger = logging.getLogger(__name__)
    logger.info('host: {}'.format(client.helpers.get_host()))

    signal.signal(signal.SIGINT, exit_gracefully)
    signal.signal(signal.SIGTERM, exit_gracefully)

    handler(args)

def exit_gracefully(*args, **kwargs):
    logger = logging.getLogger(__name__)
    logger.info('shutting down')
    exit()

if __name__ == '__main__':
    main()
