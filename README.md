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

