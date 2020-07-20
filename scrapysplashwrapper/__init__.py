#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import base64
import json
import os
import sys
from datetime import datetime
import multiprocessing
from typing import List, Dict, Any, Optional

from .middleware import ScrapySplashWrapperDepthMiddleware  # noqa
from .crawler import ScrapySplashWrapperCrawler

import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())


def crawl(splash_url: str, url: str, cookies: List[Dict[Any, Any]]=[], referer: Optional[str]=None, depth: int=1,
          user_agent: str='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
          log_enabled: bool=False, log_level: str='WARNING') -> List[Dict[Any, Any]]:
    '''Send the URL to crawl to splash, returns a list of responses from splash. Each entry from the list corresponds to a single URL loaded by Splash.'''

    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    def _crawl(queue, splash_url: str, ua: str, url: str,
               cookies: List[Dict[Any, Any]], referer: str,
               depth: int, log_enabled: bool, log_level: str) -> None:
        crawler = ScrapySplashWrapperCrawler(splash_url, ua, cookies, referer, depth, log_enabled, log_level)
        res = crawler.crawl(url)
        queue.put(res)

    q: multiprocessing.Queue[Any] = multiprocessing.Queue()
    p = multiprocessing.Process(target=_crawl, args=(q, splash_url, user_agent, url,
                                                     cookies, referer, depth,
                                                     log_enabled, log_level))
    p.start()
    res = q.get()
    p.join()
    return res


def main():
    parser = argparse.ArgumentParser(description='Crawl a URL.')
    parser.add_argument("-s", "--splash", default='http://127.0.0.1:8050', help="Splash URL to use for crawling.")
    parser.add_argument("-u", "--url", required=True, help="URL to crawl")
    parser.add_argument("-d", "--depth", default=1, help="Depth of the crawl.")
    parser.add_argument("-o", "--output", help="Output directory")
    parser.add_argument("-ua", "--useragent", help="User-Agent to use for crawling")
    parser.add_argument("--debug", action='store_true', help="Enable debug mode on scrapy/splash")

    args = parser.parse_args()
    params = {}
    if args.useragent is not None:
        params['ua'] = args.useragent
    if args.debug:
        params['log_enabled'] = True
        params['log_level'] = 'INFO'

    if args.output:
        dirpath = os.path.join('./', args.output)
    else:
        dirpath = os.path.join('./', datetime.now().isoformat())

    if os.path.exists(dirpath):
        sys.exit('{} already exists.'.format(dirpath))

    os.makedirs(dirpath)

    items = crawl(args.splash, args.url, depth=args.depth, **params)

    if not items:
        sys.exit('Unable to crawl. Probably a network problem (try --debug).')
    width = len(str(len(items)))
    i = 1
    for item in items:
        with open(os.path.join(dirpath, '{0:0{width}}.json'.format(i, width=width)), 'w') as _json:
            json.dump(item, _json)

        png = item['png']
        with open(os.path.join(dirpath, '{0:0{width}}.png'.format(i, width=width)), 'wb') as _png:
            _png.write(base64.b64decode(png))

        harfile = item['har']
        with open(os.path.join(dirpath, '{0:0{width}}.har'.format(i, width=width)), 'w') as _har:
            json.dump(harfile, _har)

        htmlfile = item['html']
        with open(os.path.join(dirpath, '{0:0{width}}.html'.format(i, width=width)), 'w') as _html:
            json.dump(htmlfile, _html)
        i += 1
