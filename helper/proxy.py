# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     Proxy
   Description :   代理对象类型封装
   Author :        JHao
   date：          2019/7/11
-------------------------------------------------
   Change Activity:
                   2019/7/11: 代理对象类型封装
-------------------------------------------------
"""
__author__ = 'JHao'

import json
import re


PROXY_ADDR_REGEX = re.compile(r"(?:.*:.*@)?(?P<ip>\d{1,3}(?:\.\d{1,3}){3}):(?P<port>\d{1,5})")


def split_proxy_addr(proxy):
    match = PROXY_ADDR_REGEX.fullmatch(proxy or "")
    if not match:
        return None, None
    return match.group("ip"), int(match.group("port"))


def normalize_asn(asn):
    if asn in (None, "", "unknown"):
        return None
    text = str(asn).strip().upper()
    return text[2:] if text.startswith("AS") else text


def format_asn(asn):
    normalized = normalize_asn(asn)
    return "AS%s" % normalized if normalized else None


def to_bool(value):
    if isinstance(value, bool):
        return value
    if value in (None, ""):
        return False
    return str(value).strip().lower() in ("true", "1", "yes")


class Proxy(object):

    def __init__(self, proxy, fail_count=0, region="", anonymous="",
                 source="", check_count=0, last_status="", last_time="", https=False,
                 ip=None, port=None, country_code=None, country_name=None, region_name=None,
                 city_name=None, asn=None, asn_org=None, isp=None, usage_type="unknown",
                 risk_score=0, risk_level="unknown", is_datacenter=False,
                 is_residential=False, is_mobile=False, is_proxy=False, is_vpn=False,
                 geo_source="unknown", risk_source="unknown", geo_updated_at=None):
        self._proxy = proxy
        parsed_ip, parsed_port = split_proxy_addr(proxy)
        self._ip = ip or parsed_ip
        self._port = int(port) if port not in (None, "") else parsed_port
        self._fail_count = fail_count
        self._region = region
        self._anonymous = anonymous
        self._source = source.split('/') if isinstance(source, str) else []
        self._check_count = check_count
        self._last_status = last_status
        self._last_time = last_time
        self._https = https
        self._country_code = country_code
        self._country_name = country_name
        self._region_name = region_name
        self._city_name = city_name
        self._asn = normalize_asn(asn)
        self._asn_org = asn_org
        self._isp = isp
        self._usage_type = usage_type or "unknown"
        self._risk_score = int(risk_score) if risk_score not in (None, "") else 0
        self._risk_level = risk_level or "unknown"
        self._is_datacenter = to_bool(is_datacenter)
        self._is_residential = to_bool(is_residential)
        self._is_mobile = to_bool(is_mobile)
        self._is_proxy = to_bool(is_proxy)
        self._is_vpn = to_bool(is_vpn)
        self._geo_source = geo_source or "unknown"
        self._risk_source = risk_source or "unknown"
        self._geo_updated_at = geo_updated_at

    @classmethod
    def createFromJson(cls, proxy_json):
        _dict = json.loads(proxy_json)
        return cls(proxy=_dict.get("proxy", ""),
                   fail_count=_dict.get("fail_count", 0),
                   region=_dict.get("region", ""),
                   anonymous=_dict.get("anonymous", ""),
                   source=_dict.get("source", ""),
                   check_count=_dict.get("check_count", 0),
                   last_status=_dict.get("last_status", ""),
                   last_time=_dict.get("last_time", ""),
                   https=_dict.get("https", False),
                   ip=_dict.get("ip"),
                   port=_dict.get("port"),
                   country_code=_dict.get("country_code"),
                   country_name=_dict.get("country_name"),
                   region_name=_dict.get("region_name"),
                   city_name=_dict.get("city_name"),
                   asn=_dict.get("asn"),
                   asn_org=_dict.get("asn_org"),
                   isp=_dict.get("isp"),
                   usage_type=_dict.get("usage_type", "unknown"),
                   risk_score=_dict.get("risk_score", 0),
                   risk_level=_dict.get("risk_level", "unknown"),
                   is_datacenter=_dict.get("is_datacenter", False),
                   is_residential=_dict.get("is_residential", False),
                   is_mobile=_dict.get("is_mobile", False),
                   is_proxy=_dict.get("is_proxy", False),
                   is_vpn=_dict.get("is_vpn", False),
                   geo_source=_dict.get("geo_source", "unknown"),
                   risk_source=_dict.get("risk_source", "unknown"),
                   geo_updated_at=_dict.get("geo_updated_at")
                   )

    @property
    def proxy(self):
        """ 代理 ip:port """
        return self._proxy

    @property
    def fail_count(self):
        """ 检测失败次数 """
        return self._fail_count

    @property
    def ip(self):
        """ 代理 IP """
        return self._ip

    @property
    def port(self):
        """ 代理端口 """
        return self._port

    @property
    def region(self):
        """ 地理位置(国家/城市) """
        return self._region

    @property
    def anonymous(self):
        """ 匿名 """
        return self._anonymous

    @property
    def source(self):
        """ 代理来源 """
        return '/'.join(self._source)

    @property
    def check_count(self):
        """ 代理检测次数 """
        return self._check_count

    @property
    def last_status(self):
        """ 最后一次检测结果  True -> 可用; False -> 不可用"""
        return self._last_status

    @property
    def last_time(self):
        """ 最后一次检测时间 """
        return self._last_time

    @property
    def https(self):
        """ 是否支持https """
        return self._https

    @property
    def country_code(self):
        return self._country_code

    @property
    def country_name(self):
        return self._country_name

    @property
    def region_name(self):
        return self._region_name

    @property
    def city_name(self):
        return self._city_name

    @property
    def asn(self):
        return format_asn(self._asn)

    @property
    def asn_org(self):
        return self._asn_org

    @property
    def isp(self):
        return self._isp

    @property
    def usage_type(self):
        return self._usage_type

    @property
    def risk_score(self):
        return self._risk_score

    @property
    def risk_level(self):
        return self._risk_level

    @property
    def is_datacenter(self):
        return self._is_datacenter

    @property
    def is_residential(self):
        return self._is_residential

    @property
    def is_mobile(self):
        return self._is_mobile

    @property
    def is_proxy(self):
        return self._is_proxy

    @property
    def is_vpn(self):
        return self._is_vpn

    @property
    def geo_source(self):
        return self._geo_source

    @property
    def risk_source(self):
        return self._risk_source

    @property
    def geo_updated_at(self):
        return self._geo_updated_at

    @property
    def to_dict(self):
        """ 属性字典 """
        return {"proxy": self.proxy,
                "ip": self.ip,
                "port": self.port,
                "https": self.https,
                "fail_count": self.fail_count,
                "region": self.region,
                "anonymous": self.anonymous,
                "country_code": self.country_code,
                "country_name": self.country_name,
                "region_name": self.region_name,
                "city_name": self.city_name,
                "asn": self.asn,
                "asn_org": self.asn_org,
                "isp": self.isp,
                "usage_type": self.usage_type,
                "risk_score": self.risk_score,
                "risk_level": self.risk_level,
                "is_datacenter": self.is_datacenter,
                "is_residential": self.is_residential,
                "is_mobile": self.is_mobile,
                "is_proxy": self.is_proxy,
                "is_vpn": self.is_vpn,
                "geo_source": self.geo_source,
                "risk_source": self.risk_source,
                "geo_updated_at": self.geo_updated_at,
                "source": self.source,
                "check_count": self.check_count,
                "last_status": self.last_status,
                "last_time": self.last_time}

    @property
    def to_json(self):
        """ 属性json格式 """
        return json.dumps(self.to_dict, ensure_ascii=False)

    @fail_count.setter
    def fail_count(self, value):
        self._fail_count = value

    @check_count.setter
    def check_count(self, value):
        self._check_count = value

    @last_status.setter
    def last_status(self, value):
        self._last_status = value

    @last_time.setter
    def last_time(self, value):
        self._last_time = value

    @https.setter
    def https(self, value):
        self._https = value

    @region.setter
    def region(self, value):
        self._region = value

    @property
    def intel_fields(self):
        return {
            "country_code": self.country_code,
            "country_name": self.country_name,
            "region_name": self.region_name,
            "city_name": self.city_name,
            "asn": self.asn,
            "asn_org": self.asn_org,
            "isp": self.isp,
            "usage_type": self.usage_type,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "is_datacenter": self.is_datacenter,
            "is_residential": self.is_residential,
            "is_mobile": self.is_mobile,
            "is_proxy": self.is_proxy,
            "is_vpn": self.is_vpn,
            "geo_source": self.geo_source,
            "risk_source": self.risk_source,
            "geo_updated_at": self.geo_updated_at,
        }

    def update_intel(self, data):
        if not data:
            return
        self._country_code = data.get("country_code", self.country_code)
        self._country_name = data.get("country_name", self.country_name)
        self._region_name = data.get("region_name", self.region_name)
        self._city_name = data.get("city_name", self.city_name)
        self._asn = normalize_asn(data.get("asn", self.asn))
        self._asn_org = data.get("asn_org", self.asn_org)
        self._isp = data.get("isp", self.isp)
        self._usage_type = data.get("usage_type", self.usage_type) or "unknown"
        self._risk_score = int(data.get("risk_score", self.risk_score) or 0)
        self._risk_level = data.get("risk_level", self.risk_level) or "unknown"
        self._is_datacenter = to_bool(data.get("is_datacenter", self.is_datacenter))
        self._is_residential = to_bool(data.get("is_residential", self.is_residential))
        self._is_mobile = to_bool(data.get("is_mobile", self.is_mobile))
        self._is_proxy = to_bool(data.get("is_proxy", self.is_proxy))
        self._is_vpn = to_bool(data.get("is_vpn", self.is_vpn))
        self._geo_source = data.get("geo_source", self.geo_source) or "unknown"
        self._risk_source = data.get("risk_source", self.risk_source) or "unknown"
        self._geo_updated_at = data.get("geo_updated_at", self.geo_updated_at)

    @source.setter
    def source(self, value):
        self._source = value.split('/') if isinstance(value, str) else []

    def add_source(self, source_str):
        if source_str:
            self._source.append(source_str)
            self._source = list(set(self._source))
