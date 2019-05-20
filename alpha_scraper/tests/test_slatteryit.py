from __future__ import absolute_import, print_function

import json
from itertools import chain
from os import path, listdir
from platform import python_version_tuple
from unittest import TestCase, main as unittest_main

from six import iteritems

from alpha_scraper.parsers.slatteryit import parsed_the_watch_archive, parsed_campaign

if python_version_tuple()[0] == '3':
    from urllib.parse import urljoin
else:
    from urlparse import urljoin

from scrapy.http import Response

from django.core.validators import URLValidator

from alpha_scraper.spiders.slatteryit import SlatteryitSpider
from alpha_scraper.utils import join_data_dir, pp
from urllib3 import PoolManager


class SlatteryITTest(TestCase):
    data_dir = join_data_dir(SlatteryitSpider.allowed_domains[0])
    html_files = frozenset(chain.from_iterable(((f for f in listdir(data_dir) if f.endswith('.html')),
                                                listdir(join_data_dir(SlatteryitSpider.allowed_domains[1])))))

    def _acquire_response(self, pathname):
        self.assertIn(pathname, self.html_files)
        res = Response(urljoin(path.basename(path.dirname(self.data_dir)), pathname[:-len('.html')]))
        fname = path.join(self.data_dir, pathname)
        parser = parsed_the_watch_archive
        if not path.isfile(fname):
            fname = join_data_dir(SlatteryitSpider.allowed_domains[1], pathname)
            parser = parsed_campaign
        with open(fname) as f:
            res._set_body(f.read())
        return parser(res)

    def test_the_watch_archive(self):
        urls = self._acquire_response('the-watch-archive.html')
        self.assertEqual(188, len(urls))
        val = URLValidator()
        for url in urls:
            self.assertIsNone(val(url))

    def test_campaign(self):

        res = self._acquire_response('3_November_2014.html')
        pp(res)

        http = PoolManager()

        for title, val in iteritems(res):
            for d in val:
                r = http.request('POST', 'http://localhost:8000/reviews/', preload_content=False,
                                 headers={'Content-Type': 'application/json'},
                                 body=json.dumps({
                                     'title': title,
                                     'named_entities': '{}'.format(d.get('named_entities')),
                                     'urls': '{}'.format(json.dumps(d['urls']) if 'urls' in d else 'None')
                                 }))
                self.assertEqual(r.status, 201, r.read())


if __name__ == '__main__':
    unittest_main()
