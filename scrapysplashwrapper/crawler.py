# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from urllib.parse import urlparse
from typing import List
from scrapy import Spider  # type: ignore
from scrapy.linkextractors import LinkExtractor  # type: ignore
from scrapy.crawler import CrawlerProcess, Crawler  # type: ignore
from scrapy import signals  # type: ignore
from scrapy_splash import SplashRequest  # type: ignore


class ScrapySplashWrapperCrawler():

    class ScrapySplashWrapperSpider(Spider):
        name = 'ScrapySplashWrapperSpider'

        def __init__(self, url: str, *args, **kwargs):
            self.start_url: str = url
            self.allowed_domains: List[str] = []
            hostname = urlparse(self.start_url).hostname
            if hostname:
                self.allowed_domains = ['.'.join(hostname.split('.')[-2:])]

        def start_requests(self):
            yield SplashRequest(self.start_url, self.parse, endpoint='render.json',
                                args={'har': 1, 'html': 1, 'response_body': 1,
                                      'png': 1, 'wait': 10, 'render_all': 1,
                                      'resource_timeout': 20, 'timeout': 80,
                                      'iframes': 1})

        def parse(self, response):
            le = LinkExtractor(allow_domains=self.allowed_domains)
            for link in le.extract_links(response):
                yield SplashRequest(link.url, self.parse, endpoint='render.json',
                                    args={'har': 1, 'html': 1, 'response_body': 1,
                                          'png': 1, 'wait': 10, 'render_all': 1,
                                          'resource_timeout': 20, 'timeout': 80,
                                          'iframes': 1})
            yield response.data

    def __init__(self, splash_url, useragent, depth=1, log_enabled=False, log_level='WARNING'):
        self.process = CrawlerProcess({'LOG_ENABLED': log_enabled})
        self.crawler = Crawler(self.ScrapySplashWrapperSpider, {
            'LOG_ENABLED': log_enabled,
            'LOG_LEVEL': log_level,
            'USER_AGENT': useragent,
            'SPLASH_URL': splash_url,
            'DOWNLOADER_MIDDLEWARES': {'scrapy_splash.SplashCookiesMiddleware': 723,
                                       'scrapy_splash.SplashMiddleware': 725,
                                       'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
                                       },
            'SPIDER_MIDDLEWARES': {'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
                                   'scrapysplashwrapper.ScrapySplashWrapperDepthMiddleware': 110},
            'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
            'DEPTH_LIMIT': depth
        })

    def crawl(self, url):
        crawled_items = []

        def add_item(item):
            crawled_items.append(item)

        self.crawler.signals.connect(add_item, signals.item_scraped)
        self.process.crawl(self.crawler, url=url)
        self.process.start()
        return crawled_items
