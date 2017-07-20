#!/usr/bin/env python3

import argparse
import logging
import logging.config
import subprocess
import yaml
import sys

from argparse import ArgumentParser
from pathlib import Path


logger = logging.getLogger(__name__)

def configure_logging(parent, args):
    """
    Configure logging (level, format, etc.) for this module

    Sensible defaults come from 'transpile.yml' and can be changed
    by values that come from console.

    :param parent: -- directory where 'transpile.yml' resides
    :param args:   -- general arguments for transpile
    """
    with open(Path(parent, 'transpile.yml'), 'r') as config:
        params = yaml.load(config)

        logging.config.dictConfig(params['logging'])

        if args.verbose == 0:
            pass  # use level specified by the config file
        elif args.verbose == 1:
            logger.setLevel(logging.INFO)
        else:
            logger.setLevel(logging.DEBUG)

        if args.quiet:
            logging.disable(logging.CRITICAL)
            # Message below should not reach the user
            logger.critical('logging is active despite --quiet')

    logger.debug('configure_logging() done')

def create_transcrypt_cmd(args, transcrypt_args):
    """
    Create a subprocess command that calls transcrypt

    :param args:            -- general arguments for transpile
    :param transcrypt_args: -- arguments specific to transcrypt

    :returns: a command line suitable for subprocess.run()
    """
    logger.debug('create_transcrypt_cmd() call')

    # Assume transcrypt executable is ../bin/transcrypt, full path:
    cmd = [str(Path(
        Path(__file__).resolve().parent.parent, 'bin', 'transcrypt'
    ))]

    # You can specify '--' on the command line to pass parameters
    # directly to transcrypt, example: transpile -- --help
    # In this case '--' is also passed first, so need to remove it:
    if transcrypt_args and transcrypt_args[0] == '--':
        transcrypt_args = transcrypt_args[1:]

    cmd += transcrypt_args

    # If you are manually passing transcrypt arguments, please specify
    # them all yourself. Otherwise, let me provide sensible defaults:
    if not transcrypt_args:
        # Force transpiling from scratch
        cmd.append("-b")
        # Force EcmaScript 6 for generator support
        cmd.append("-e 6")
        cmd.append(str(args.src[0]))

    logger.info('constructed the following command')
    logger.info(str(cmd))

    logger.debug('create_transcrypt_cmd() done')
    return cmd

def transpile():
    """
    Call transcrypt to transpile boolean.py into JavaScript
    """

    fpath = Path(__file__).resolve()
    parent = fpath.parent

    parser = ArgumentParser(
        prog=fpath.name,
        description="Transpile boolean.py into JavaScript"
    )

    # source path, directory where license_expression resides
    spath = Path(parent.parent, 'src', 'license_expression')

    # license_expression path
    lpath = Path(spath, '__init__.py')
    parser.add_argument(
        '--src', nargs=1, default=[lpath],
        help='start transpilation from here'
    )

    # javascript path, for output
    jpath = Path(spath, '__javascript__')
    parser.add_argument(
        '--dst', nargs=1, default=[jpath],
        help='store produced javascript here'
    )

    parser.add_argument(
        '-v', '--verbose', action='count',
        help='print more output information'
    )

    parser.add_argument(
        '-q', '--quiet', action='store_true',
        help='print nothing (transcrypt might print though)'
    )

    args, transcrypt_args = parser.parse_known_args()

    configure_logging(parent, args)

    # User can specify '--quiet' to suppress output. So, delay any
    # logging calls until we know the desired verbosity level.
    logger.debug('transpile() call')

    logger.debug('.parse_known_args() call')
    logger.debug('src            : ' + str(args.src))
    logger.debug('dst            : ' + str(args.dst))
    logger.debug('transcrypt_args: ' + str(transcrypt_args))
    logger.debug('.parse_known_args() done')

    cmd = create_transcrypt_cmd(args, transcrypt_args)

    logger.debug('subprocess.run() call')
    process = subprocess.run(cmd)
    logger.debug('subprocess.run() done')

    if process.returncode != 0:
        logger.warning('Transcrypt failed:')

        for line in str(process.stdout).split('\\n'):
            logger.warning(line)
        for line in str(process.stderr).split('\\n'):
            logger.warning(line)

        sys.exit(1)

    logger.debug(process.stdout)
    logger.debug(process.stderr)

    logger.debug('transpile() done')

if __name__ == "__main__":
    transpile()