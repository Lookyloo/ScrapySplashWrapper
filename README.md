[![Documentation Status](https://readthedocs.org/projects/scrapysplashwrapper/badge/?version=latest)](https://scrapysplashwrapper.readthedocs.io/en/latest/?badge=latest)

**IMPORTANT**: This project isn't used by lookyloo anymore. It has been supersedded by the [playwright capture module](https://github.com/Lookyloo/PlaywrightCapture) because [splash](https://github.com/scrapinghub/splash) isn't maintained and isn't able to capture properly more and more websites (it uses webkit from 2016).
If you rely on this dependency for anything, you should look at the playwright capture module, and/or consider forking and maintaining it as it won't be monitored anymore.

# ScrapySplashWrapper
A wrapper that uses scrappy and splash to crawl a website.

# Usage

*Warning*: it requires a splash instance (docker is recommendended).

```
usage: scraper [-h] [-s SPLASH] -u URL [-d DEPTH] [-o OUTPUT] [-ua USERAGENT]
               [--debug]

Crawl a URL.

optional arguments:
  -h, --help            show this help message and exit
  -s SPLASH, --splash SPLASH
                        Splash URL to use for crawling.
  -u URL, --url URL     URL to crawl
  -d DEPTH, --depth DEPTH
                        Depth of the crawl.
  -o OUTPUT, --output OUTPUT
                        Output directory
  -ua USERAGENT, --useragent USERAGENT
                        User-Agent to use for crawling
  --debug               Enable debug mode on scrapy/splash

```
