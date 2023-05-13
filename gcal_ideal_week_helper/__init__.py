"""This module demonstrates basic Sphinx usage with Python modules.



"""

__author__ = 'Riccardo Petraglia'
__email__ = 'riccardo.petraglia@gmail.com'
__version__ = '0.1.0'

import os
import logging.config
import yaml
from pathlib import Path


def logger_setup(
          default_path=Path(__file__).resolve().parents[1] / 'logging.yaml',
          default_level=logging.INFO,
          env_key='LOG_CFG'):
    """Setup logging configuration

    """
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
