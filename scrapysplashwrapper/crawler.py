# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

from urllib.parse import urlparse
from typing import List, Iterator
from scrapy import Spider  # type: ignore
from scrapy.linkextractors import LinkExtractor  # type: ignore
from scrapy.crawler import CrawlerProcess, Crawler  # type: ignore
from scrapy import signals  # type: ignore
from scrapy_splash import SplashRequest, SplashJsonResponse  # type: ignore

script = """
function main(splash, args)
    -- Default values
    splash.js_enabled = true
    splash.private_mode_enabled = true
    splash.images_enabled = true
    splash.webgl_enabled = true
    splash.media_source_enabled = true

    -- Force enable things
    splash.plugins_enabled = true
    splash.request_body_enabled = true
    splash.response_body_enabled = true

    -- Would be nice
    splash.indexeddb_enabled = true
    splash.html5_media_enabled = true
    splash.http2_enabled = true

    -- User defined
    splash.resource_timeout = args.resource_timeout
    splash.timeout = args.timeout
    splash:set_user_agent(args.useragent)

   -- Allow to pass cookies
    splash:init_cookies(args.cookies)

    -- Run
    ok, reason = splash:go{args.url}
    -- The error options are listed here: https://splash.readthedocs.io/en/stable/scripting-ref.html#splash-go
    -- HTTP errors are fine, we keep going.
    if not ok and not reason:find("http") then
        return {error = reason}
    end
    splash:wait{args.wait}

    -- Page instrumentation
    splash.scroll_position = {y=1000}

    splash:wait{args.wait}

    -- Response
    return {
        har = splash:har(),
        html = splash:html(),
        png = splash:png{render_all=true},
        cookies = splash:get_cookies()
    }

end
"""


class ScrapySplashWrapperCrawler():

    class ScrapySplashWrapperSpider(Spider):
        name = 'ScrapySplashWrapperSpider'

        def __init__(self, url: str, useragent: str, cookies: List[dict]=[], *args, **kwargs):
            self.start_url: str = url
            self.useragent: str = useragent
            self.allowed_domains: List[str] = []
            self.cookies: List[dict] = cookies
            hostname = urlparse(self.start_url).hostname
            if hostname:
                self.allowed_domains = ['.'.join(hostname.split('.')[-2:])]

        def start_requests(self):
            yield SplashRequest(self.start_url, self.parse, endpoint='execute',
                                args={'wait': 15, 'resource_timeout': 40,
                                      'timeout': 60,
                                      'useragent': self.useragent,
                                      'cookies': self.cookies,
                                      'lua_source': script
                                      })

        def parse(self, response: SplashJsonResponse) -> Iterator[dict]:
            le = LinkExtractor(allow_domains=self.allowed_domains)
            for link in le.extract_links(response):
                yield SplashRequest(link.url, self.parse, endpoint='execute',
                                    args={'wait': 10, 'resource_timeout': 20,
                                          'useragent': self.useragent,
                                          'cookies': response.data['cookies'],
                                          'lua_source': script
                                          })
            yield response.data

    def __init__(self, splash_url: str, useragent: str, cookies: List[dict]=[], depth: int=1, log_enabled: bool=False, log_level: str='WARNING'):
        self.useragent = useragent
        self.cookies = cookies
        self.process = CrawlerProcess({'LOG_ENABLED': log_enabled})
        self.crawler = Crawler(self.ScrapySplashWrapperSpider, {
            'LOG_ENABLED': log_enabled,
            'LOG_LEVEL': log_level,
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
        self.process.crawl(self.crawler, url=url, useragent=self.useragent, cookies=self.cookies)
        self.process.start()
        return crawled_items
