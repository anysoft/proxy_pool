# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     ProxyHandler.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/03:
                   2020/05/26: 区分http和https
-------------------------------------------------
"""
__author__ = 'JHao'

from helper.proxy import Proxy
from helper.ip_intel import lookup
from db.dbClient import DbClient
from handler.logHandler import LogHandler
from handler.configHandler import ConfigHandler


class ProxyHandler(object):
    """ Proxy CRUD operator"""

    def __init__(self):
        self.conf = ConfigHandler()
        self.log = LogHandler("proxy_handler")
        self.db = DbClient(self.conf.dbConn)
        self.db.changeTable(self.conf.tableName)

    @staticmethod
    def has_useful_intel(proxy):
        return bool(proxy and proxy.geo_source and proxy.geo_source != "unknown")

    def enrich(self, proxy):
        """
        Fill IP intelligence fields before storing a proxy.
        Existing profile fields for the same proxy are reused first to avoid
        repeated MMDB lookups.
        """
        if not self.conf.enableIpIntel or not proxy or not proxy.ip:
            return proxy
        try:
            exists = self.db.getByProxy(proxy.proxy)
            if exists:
                old_proxy = Proxy.createFromJson(exists)
                if self.has_useful_intel(old_proxy):
                    proxy.update_intel(old_proxy.intel_fields)
                    return proxy
            for item in self.getAll(False):
                if item.ip == proxy.ip and self.has_useful_intel(item):
                    proxy.update_intel(item.intel_fields)
                    return proxy
            proxy.update_intel(lookup(proxy.ip))
        except Exception as e:
            self.log.error("enrich proxy %s failed: %s" % (proxy.proxy, str(e)))
        return proxy

    def enrichAll(self, force=False):
        """
        Backfill IP intelligence for proxies already stored in DB.
        Args:
            force: refresh all proxies when True; otherwise only unknown entries.
        """
        result = {"total": 0, "updated": 0, "skipped": 0, "failed": 0}
        for proxy in self.getAll(False):
            result["total"] += 1
            if not force and self.has_useful_intel(proxy):
                result["skipped"] += 1
                continue
            try:
                proxy.update_intel(lookup(proxy.ip))
                self.db.put(proxy)
                result["updated"] += 1
            except Exception as e:
                self.log.error("backfill proxy %s failed: %s" % (proxy.proxy, str(e)))
                result["failed"] += 1
        return result

    def get(self, https=False):
        """
        return a proxy
        Args:
            https: True/False
        Returns:
        """
        proxy = self.db.get(https)
        return Proxy.createFromJson(proxy) if proxy else None

    def pop(self, https):
        """
        return and delete a useful proxy
        :return:
        """
        proxy = self.db.pop(https)
        if proxy:
            return Proxy.createFromJson(proxy)
        return None

    def put(self, proxy):
        """
        put proxy into use proxy
        :return:
        """
        proxy = self.enrich(proxy)
        self.db.put(proxy)

    def delete(self, proxy):
        """
        delete useful proxy
        :param proxy:
        :return:
        """
        return self.db.delete(proxy.proxy)

    def getAll(self, https=False):
        """
        get all proxy from pool as Proxy list
        :return:
        """
        proxies = self.db.getAll(https)
        return [Proxy.createFromJson(_) for _ in proxies]

    def exists(self, proxy):
        """
        check proxy exists
        :param proxy:
        :return:
        """
        return self.db.exists(proxy.proxy)

    def getCount(self):
        """
        return raw_proxy and use_proxy count
        :return:
        """
        total_use_proxy = self.db.getCount()
        return {'count': total_use_proxy}
