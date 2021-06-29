#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ScrapySplashWrapperError(Exception):
    """Base class for other exceptions"""
    pass


class InvalidProxy(ScrapySplashWrapperError):
    """Raised when the proxy is not valid"""

    def __init__(self, proxy: str, message_details: str=''):
        self.default_message = f'The proxy ({proxy}) is not in a valid format. Should be [scheme]://[username]:[password]@[hostname]:[port].'
        if message_details:
            self.message = f'{message_details} {self.default_message}'
        else:
            self.message = self.default_message
