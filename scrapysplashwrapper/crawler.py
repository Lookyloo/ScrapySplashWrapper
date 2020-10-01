# -*- coding: utf-8 -*-
# This file is part of Viper - https://github.com/viper-framework/viper
# See the file 'LICENSE' for copying permission.

import os
from pathlib import Path
import logging
from urllib.parse import urlparse
from typing import List, Iterator, Dict, Any
from scrapy import Spider  # type: ignore
from scrapy.linkextractors import LinkExtractor  # type: ignore
from scrapy.crawler import CrawlerProcess, Crawler  # type: ignore
from scrapy import signals
from scrapy_splash import SplashRequest, SplashJsonResponse  # type: ignore

# Mapping from https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum
error_mapping = {
    'http': "HTTP Error {}",
    "network1": "the remote server refused the connection (the server is not accepting requests)",
    "network2": "the remote server closed the connection prematurely, before the entire reply was received and processed",
    "network3": "the remote host name was not found (invalid hostname)",
    "network4": "the connection to the remote server timed out",
    "network5": "the operation was canceled via calls to abort() or close() before it was finished.",
    "network6": "the SSL/TLS handshake failed and the encrypted channel could not be established. The sslErrors() signal should have been emitted.",
    "network7": "the connection was broken due to disconnection from the network, however the system has initiated roaming to another access point. The request should be resubmitted and will be processed as soon as the connection is re-established.",
    "network8": "the connection was broken due to disconnection from the network or failure to start the network.",
    "network9": "the background request is not currently allowed due to platform policy.",
    "network10": "while following redirects, the maximum limit was reached. The limit is by default set to 50 or as set by QNetworkRequest::setMaxRedirectsAllowed(). (This value was introduced in 5.6.)",
    "network11": "while following redirects, the network access API detected a redirect from a encrypted protocol (https) to an unencrypted one (http). (This value was introduced in 5.6.)",
    "network101": "the connection to the proxy server was refused (the proxy server is not accepting requests)",
    "network102": "the proxy server closed the connection prematurely, before the entire reply was received and processed",
    "network103": "the proxy host name was not found (invalid proxy hostname)",
    "network104": "the connection to the proxy timed out or the proxy did not reply in time to the request sent",
    "network105": "the proxy requires authentication in order to honour the request but did not accept any credentials offered (if any)",
    "network201": "the access to the remote content was denied (similar to HTTP error 403)",
    "network202": "the operation requested on the remote content is not permitted",
    "network203": "the remote content was not found at the server (similar to HTTP error 404)",
    "network204": "the remote server requires authentication to serve the content but the credentials provided were not accepted (if any)",
    "network205": "the request needed to be sent again, but this failed for example because the upload data could not be read a second time.",
    "network206": "the request could not be completed due to a conflict with the current state of the resource.",
    "network207": "the requested resource is no longer available at the server.",
    "network401": "the server encountered an unexpected condition which prevented it from fulfilling the request.",
    "network402": "the server does not support the functionality required to fulfill the request.",
    "network403": "the server is unable to handle the request at this time.",
    "network301": "the Network Access API cannot honor the request because the protocol is not known",
    "network302": "the requested operation is invalid for this protocol",
    "network99": "an unknown network-related error was detected",
    "network199": "an unknown proxy-related error was detected",
    "network299": "an unknown error related to the remote content was detected",
    "network399": "a breakdown in protocol was detected (parsing error, invalid or unexpected responses, etc.)",
    "network499": "an unknown error related to the server response was detected"
}


class ScrapySplashWrapperCrawler():

    class ScrapySplashWrapperSpider(Spider):
        name = 'ScrapySplashWrapperSpider'
        handle_httpstatus_all = True  # https://docs.scrapy.org/en/latest/topics/spider-middleware.html?highlight=handle_httpstatus_all#std-reqmeta-handle_httpstatus_all

        def __init__(self, url: str, useragent: str, cookies: List[Dict[Any, Any]]=[], referer: str='', log_level: str='WARNING', *args, **kwargs) -> None:
            logger = logging.getLogger('scrapy')
            logger.setLevel(log_level)
            super().__init__(*args, **kwargs)
            self.start_url: str = url
            self.useragent: str = useragent
            self.allowed_domains: List[str] = []
            self.cookies: List[Dict[Any, Any]] = cookies
            self.referer: str = referer
            hostname = urlparse(self.start_url).hostname
            if hostname:
                self.allowed_domains = ['.'.join(hostname.split('.')[-2:])]
            realpath = Path(os.path.realpath(__file__)).parent
            with (realpath / 'crawl.lua').open() as _crawl:
                self.script = _crawl.read()

        def start_requests(self):
            yield SplashRequest(self.start_url, self.parse, endpoint='execute',
                                args={'wait': 15, 'resource_timeout': 40,
                                      'timeout': 90,
                                      'useragent': self.useragent,
                                      'referer': self.referer,
                                      'cookies': [{k: v for k, v in cookie.items() if v is not None} for cookie in self.cookies],
                                      'lua_source': self.script
                                      })

        def parse(self, response: SplashJsonResponse) -> Iterator[Dict[Any, Any]]:
            le = LinkExtractor(allow_domains=self.allowed_domains)
            for link in le.extract_links(response):
                yield SplashRequest(link.url, self.parse, endpoint='execute',
                                    args={'wait': 10, 'resource_timeout': 20,
                                          'useragent': self.useragent,
                                          'referer': response.data['last_redirected_url'],
                                          'cookies': response.data['cookies'],
                                          'lua_source': self.script
                                          })
            yield response.data

    def __init__(self, splash_url: str, useragent: str, cookies: List[Dict[Any, Any]]=[], referer: str='', depth: int=1, log_enabled: bool=False, log_level: str='WARNING'):
        self.useragent = useragent
        self.cookies = cookies
        self.referer = referer
        self.log_level = log_level
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

    def crawl(self, url: str) -> List[Any]:
        crawled_items = []

        def add_item(item) -> None:
            if 'error' in item:
                key = item.pop('error')
                error = {'key': key, 'details': "Unknown error, see https://doc.qt.io/qt-5/qnetworkreply.html#NetworkError-enum"}
                if key.startswith('http'):
                    error['details'] = error_mapping['http'].format(key[4:])
                elif key.startswith('network'):
                    details = error_mapping.get(key)
                    if details:
                        error['details'] = details
                item['error'] = error

            crawled_items.append(item)

        self.crawler.signals.connect(add_item, signals.item_scraped)
        self.process.crawl(self.crawler, url=url, useragent=self.useragent, cookies=self.cookies, referer=self.referer, log_level=self.log_level)
        self.process.start()
        return crawled_items
