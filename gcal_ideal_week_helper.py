#!/usr/bin/env python3
"""
Module Docstring
"""

__author__ = "Riccardo Petraglia"
__version__ = "0.1.0"
__email__ = "riccardo.petraglia@gmail.com"

import argparse
import logging
import os

from google.auth.exceptions import RefreshError

import gcal_ideal_week_helper

import gcal_ideal_week_helper.authorization
import gcal_ideal_week_helper.compute

gcal_ideal_week_helper.logger_setup()
log = logging.getLogger('main')
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))


def main(args):
    """ Main entry point of the app """
    try:
        creds = gcal_ideal_week_helper.authorization.credentials(ROOT_DIR)
    except RefreshError as e:
        os.remove('token.json')
        creds = gcal_ideal_week_helper.authorization.credentials(ROOT_DIR)
        if creds is None:
            raise e

    gcal_ideal_week_helper.compute.run_example(creds, args.calendar_name)

    return "Do some magic!"


if __name__ == "__main__":
    """ This is executed when run from the command line """
    parser = argparse.ArgumentParser()

    # Required positional argument
    parser.add_argument("calendar_name", help="Required positional argument")

    # Optional argument flag which defaults to False
    parser.add_argument("-f", "--flag", action="store_true", default=False)

    # Optional argument which requires a parameter (eg. -d test)
    parser.add_argument("-n", "--name", action="store", dest="name")

    # Optional verbosity counter (eg. -v, -vv, -vvv, etc.)
    parser.add_argument("-v", "--verbose",
                        action="count",
                        default=0,
                        help="Verbosity (-v, -vv, etc)")

    # Specify output of "--version"
    parser.add_argument("--version",
                        action="version",
                        version="%(prog)s (version {version})".format(version=__version__))

    args = parser.parse_args()
    main(args)
