from __future__ import print_function

# from codecs import open
from functools import partial
from os import environ, path, makedirs
from platform import python_version_tuple
from sys import modules
from pprint import PrettyPrinter

from bs4 import BeautifulSoup
from pkg_resources import resource_filename

from alpha_scraper import get_logger
from alpha_scraper.parsers.slatteryit import get_date_name

if python_version_tuple()[0] == '3':
    from urllib.parse import urlparse
else:
    from urlparse import urlparse


pp = PrettyPrinter(indent=4).pprint

join_data_dir = partial(path.join,
                        resource_filename(modules[__name__].__name__, path.join('_data')))
logger = get_logger(name=modules[__name__].__name__)


def cache_response(pretty=False):
    def outer(func):
        def inner(self, response):
            if not environ.get('CACHE_HTML'):
                return func(self, response)

            parsed_url = urlparse(response.url)
            domain = parsed_url.netloc.replace('www.', '')
            pathname = parsed_url.path.replace('/', '')
            html_path = '{}.html'.format(get_date_name(response) if domain == 'us8.campaign-archive.com' else pathname)
            directory = join_data_dir(domain)
            if not path.isdir(directory):
                makedirs(directory)
            cache_fname = path.join(directory, html_path)

            logger.info('Caching to: {}'.format(cache_fname))

            if pretty:
                response._set_body(BeautifulSoup(response.body, 'html.parser').prettify(encoding='utf8'))

            with open(cache_fname, mode='wt') as f:
                f.write(response.body)

            return func(self, response)

        return inner

    return outer
