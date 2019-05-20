# -*- coding: utf-8 -*-
from __future__ import print_function

from platform import python_version_tuple
from sys import modules

from scrapy import Request

from alpha_scraper import get_logger
from alpha_scraper.parsers.slatteryit import parsed_the_watch_archive, parsed_campaign

if python_version_tuple()[0] == '3':
    from urllib.parse import urlparse
else:
    from urlparse import urlparse

import scrapy
from scrapy_splash import SplashRequest

from alpha_scraper.utils import cache_response

logger = get_logger(name=modules[__name__].__name__)


class SlatteryitSpider(scrapy.Spider):
    name = 'SlatteryitSpider'
    allowed_domains = 'slatteryit.com.au', 'us8.campaign-archive.com'
    start_urls = 'http://www.slatteryit.com.au/the-watch-archive/',

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, self.parse_root, args={'wait': 0.5})

    @cache_response(pretty=True)
    def parse_root(self, response):
        pathname = urlparse(response.url).path.replace('/', '')

        if pathname == 'the-watch-archive':
            newsletters = parsed_the_watch_archive(response)
            yield {'newsletters': newsletters}
            for url in newsletters:
                yield Request(url, callback=self.parse_campaign)
        else:
            logger.warn('parse_root::Unclear how to parse: {}'.format(response.url))

    @cache_response(pretty=True)
    def parse_campaign(self, response):
        yield parsed_campaign(response)
