#!/usr/bin/env python

import logging
from functools import partial
from logging.config import dictConfig as _dictConfig
from os import path
from sys import modules

import yaml
from pkg_resources import resource_filename

__author__ = 'Samuel Marks'
__version__ = '0.0.1'


def get_logger(name=None):
    with open(path.join(path.dirname(__file__), '_data', 'logging.yml'), 'rt') as f:
        data = yaml.load(f)
    _dictConfig(data)
    return logging.getLogger(name=name)


root_logger = get_logger()
