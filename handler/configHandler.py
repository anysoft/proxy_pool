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
    def httpsUrl(self):
        return os.getenv("HTTPS_URL", setting.HTTPS_URL)

    @LazyProperty
    def verifyTimeout(self):
        return int(os.getenv("VERIFY_TIMEOUT", setting.VERIFY_TIMEOUT))

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
    def fetchSchedulerWorkers(self):
        return int(os.getenv("FETCH_SCHEDULER_WORKERS", setting.FETCH_SCHEDULER_WORKERS))

    @LazyProperty
    def proxyCheckerThreadCount(self):
        return int(os.getenv("PROXY_CHECKER_THREAD_COUNT", setting.PROXY_CHECKER_THREAD_COUNT))

    @LazyProperty
    def proxyRegion(self):
        return bool(os.getenv("PROXY_REGION", setting.PROXY_REGION))

    @LazyProperty
    def timezone(self):
        return os.getenv("TIMEZONE", setting.TIMEZONE)

    @LazyProperty
    def enableIpIntel(self):
        return str(os.getenv("ENABLE_IP_INTEL", setting.ENABLE_IP_INTEL)).lower() in ("true", "1", "yes")

    @LazyProperty
    def enableOnlineIpLookup(self):
        return str(os.getenv("ENABLE_ONLINE_IP_LOOKUP", setting.ENABLE_ONLINE_IP_LOOKUP)).lower() in ("true", "1", "yes")

    @LazyProperty
    def geoipCountryDb(self):
        return os.getenv("GEOIP_COUNTRY_DB", setting.GEOIP_COUNTRY_DB)

    @LazyProperty
    def geoipCityDb(self):
        return os.getenv("GEOIP_CITY_DB", setting.GEOIP_CITY_DB)

    @LazyProperty
    def geoipAsnDb(self):
        return os.getenv("GEOIP_ASN_DB", setting.GEOIP_ASN_DB)

    @LazyProperty
    def ipIntelCacheSize(self):
        return int(os.getenv("IP_INTEL_CACHE_SIZE", setting.IP_INTEL_CACHE_SIZE))

    @LazyProperty
    def enableRiskRules(self):
        return str(os.getenv("ENABLE_RISK_RULES", setting.ENABLE_RISK_RULES)).lower() in ("true", "1", "yes")

    @property
    def datacenterKeywords(self):
        reload_six(setting)
        return setting.DATACENTER_KEYWORDS

    @property
    def mobileKeywords(self):
        reload_six(setting)
        return setting.MOBILE_KEYWORDS

    @property
    def residentialKeywords(self):
        reload_six(setting)
        return setting.RESIDENTIAL_KEYWORDS

    @LazyProperty
    def ipinfoToken(self):
        return os.getenv("IPINFO_TOKEN", setting.IPINFO_TOKEN)

    @LazyProperty
    def ipqualityscoreToken(self):
        return os.getenv("IPQUALITYSCORE_TOKEN", setting.IPQUALITYSCORE_TOKEN)
