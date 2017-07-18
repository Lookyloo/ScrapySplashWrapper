__version__ = '0.1'

from .middleware import ScrapySplashWrapperDepthMiddleware  # flake8: noqa
from .crawler import ScrapySplashWrapperCrawler
import multiprocessing


def crawl(splash_url, url, depth=1,
          user_agent='Mozilla/5.0 (Windows NT 6.3; WOW64; rv:53.0) Gecko/20100101 Firefox/53.0',
          log_enabled=False, log_level='WARNING'):
    def _crawl(queue, splash_url, ua, url, depth, log_enabled, log_level):
        crawler = ScrapySplashWrapperCrawler(splash_url, ua, depth, log_enabled, log_level)
        res = crawler.crawl(url)
        queue.put(res)

    q = multiprocessing.Queue()
    p = multiprocessing.Process(target=_crawl, args=(q, splash_url, user_agent, url,
                                                     depth, log_enabled, log_level))
    p.start()
    res = q.get()
    p.join()
    return res
