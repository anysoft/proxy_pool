# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     configHandler
   Description :
   Author :        JHao
   date：          2020/6/22
-------------------------------------------------
   Change Activity:
                   2020/6/22:
-------------------------------------------------
"""
__author__ = 'JHao'

import os
import setting
from util.singleton import Singleton
from util.lazyProperty import LazyProperty
from util.six import reload_six, withMetaclass


class ConfigHandler(withMetaclass(Singleton)):

    def __init__(self):
        pass

    @LazyProperty
    def serverHost(self):
        return os.environ.get("HOST", setting.HOST)

    @LazyProperty
    def serverPort(self):
        return os.environ.get("PORT", setting.PORT)

    @LazyProperty
    def dbConn(self):
        return os.getenv("DB_CONN", setting.DB_CONN)

    @LazyProperty
    def tableName(self):
        return os.getenv("TABLE_NAME", setting.TABLE_NAME)

    @property
    def fetchers(self):
        reload_six(setting)
        return setting.PROXY_FETCHER

    @LazyProperty
    def httpUrl(self):
        return os.getenv("HTTP_URL", setting.HTTP_URL)

    @LazyProperty
    def httpUrlHeader(self):
        return os.getenv("HTTP_URL_HEADER", setting.HTTP_URL_HEADER)

    @LazyProperty
    def httpsUrl(self):
        return os.getenv("HTTPS_URL", setting.HTTPS_URL)

    @LazyProperty
    def httpsUrlHeader(self):
        return os.getenv("HTTPS_URL_HEADER", setting.HTTPS_URL_HEADER)
    @LazyProperty
    def httpsUrlBody(self):
        return os.getenv("HTTPS_URL_BODY", setting.HTTPS_URL_BODY)

    @LazyProperty
    def connectTimeout(self):
        return int(os.getenv("CONNECT_TIMEOUT", setting.CONNECT_TIMEOUT))

    @LazyProperty
    def readTimeout(self):
        return int(os.getenv("READ_TIMEOUT", setting.READ_TIMEOUT))

    # @LazyProperty
    # def proxyCheckCount(self):
    #     return int(os.getenv("PROXY_CHECK_COUNT", setting.PROXY_CHECK_COUNT))

    @LazyProperty
    def maxFailCount(self):
        return int(os.getenv("MAX_FAIL_COUNT", setting.MAX_FAIL_COUNT))

    # @LazyProperty
    # def maxFailRate(self):
    #     return int(os.getenv("MAX_FAIL_RATE", setting.MAX_FAIL_RATE))

    @LazyProperty
    def poolSizeMin(self):
        return int(os.getenv("POOL_SIZE_MIN", setting.POOL_SIZE_MIN))
    @LazyProperty
    def proxyFetchInterval(self):
        return int(os.getenv("PROXY_FETCH_INTERVAL", setting.PROXY_FETCH_INTERVAL))
    @LazyProperty
    def proxyCheckInterval(self):
        return int(os.getenv("PROXY_CHECK_INTERVAL", setting.PROXY_CHECK_INTERVAL))

    @LazyProperty
    def proxyRegion(self):
        return bool(os.getenv("PROXY_REGION", setting.PROXY_REGION))

    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)
