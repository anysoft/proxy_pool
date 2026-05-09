# -*- coding: utf-8 -*-
"""
Offline IP intelligence helpers.

The module prefers local MMDB files and always degrades to conservative
"unknown" values when a database, dependency, or lookup is unavailable.
"""
from __future__ import absolute_import

import os
from datetime import datetime

try:
    from functools import lru_cache
except ImportError:
    def lru_cache(maxsize=128):
        def decorator(func):
            cache = {}

            def wrapper(arg):
                if arg in cache:
                    return cache[arg]
                if len(cache) >= maxsize:
                    cache.pop(next(iter(cache)))
                cache[arg] = func(arg)
                return cache[arg]
            return wrapper
        return decorator

from handler.configHandler import ConfigHandler
from handler.logHandler import LogHandler
from helper.proxy import format_asn

try:
    import geoip2.database
except Exception:
    geoip2 = None


log = LogHandler("ip_intel")
conf = ConfigHandler()
_READERS = {}
_READER_INIT_DONE = False


def unknown_result(ip=None):
    return {
        "ip": ip,
        "country_code": None,
        "country_name": None,
        "region_name": None,
        "city_name": None,
        "asn": None,
        "asn_org": None,
        "isp": None,
        "usage_type": "unknown",
        "risk_score": 50,
        "risk_level": "unknown",
        "is_datacenter": False,
        "is_residential": False,
        "is_mobile": False,
        "is_proxy": False,
        "is_vpn": False,
        "geo_source": "unknown",
        "risk_source": "offline_rule",
        "geo_updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def _open_reader(name, path):
    if not path or not os.path.exists(path):
        log.info("GeoIP %s db not found, skip: %s" % (name, path))
        return None
    if geoip2 is None:
        log.info("geoip2 is not installed, skip GeoIP %s db: %s" % (name, path))
        return None
    try:
        reader = geoip2.database.Reader(path)
        log.info("GeoIP %s db loaded: %s" % (name, path))
        return reader
    except Exception as e:
        log.error("GeoIP %s db load failed: %s" % (name, str(e)))
        return None


def _init_readers():
    global _READER_INIT_DONE
    if _READER_INIT_DONE:
        return
    _READER_INIT_DONE = True
    if not conf.enableIpIntel:
        log.info("IP intelligence disabled by ENABLE_IP_INTEL")
        return
    _READERS["country"] = _open_reader("country", conf.geoipCountryDb)
    _READERS["city"] = _open_reader("city", conf.geoipCityDb)
    _READERS["asn"] = _open_reader("asn", conf.geoipAsnDb)


def status():
    """
    Return local GeoIP dependency and database status for API diagnostics.
    """
    _init_readers()
    items = []
    for name, path in (
        ("country", conf.geoipCountryDb),
        ("city", conf.geoipCityDb),
        ("asn", conf.geoipAsnDb),
    ):
        items.append({
            "name": name,
            "path": path,
            "exists": bool(path and os.path.exists(path)),
            "loaded": bool(_READERS.get(name)),
        })
    return {
        "enable_ip_intel": conf.enableIpIntel,
        "enable_risk_rules": conf.enableRiskRules,
        "geoip2_available": geoip2 is not None,
        "cache_size": conf.ipIntelCacheSize,
        "databases": items,
    }


def _contains_keyword(text, keywords):
    target = (text or "").lower()
    if not target or target == "unknown":
        return False
    return any(keyword.lower() in target for keyword in keywords)


def apply_risk_rules(data):
    result = data.copy()
    text = " ".join([result.get("asn_org") or "", result.get("isp") or ""]).lower()

    if _contains_keyword(text, conf.datacenterKeywords):
        result.update({
            "usage_type": "datacenter",
            "is_datacenter": True,
            "is_residential": False,
            "is_mobile": False,
            "risk_score": max(int(result.get("risk_score") or 0), 80),
            "risk_level": "high",
            "risk_source": "offline_rule",
        })
        return result

    if _contains_keyword(text, conf.mobileKeywords):
        score = result.get("risk_score")
        result.update({
            "usage_type": "mobile",
            "is_datacenter": False,
            "is_mobile": True,
            "risk_score": 30 if score in (None, "", 0, 50) else int(score),
            "risk_level": result.get("risk_level") if result.get("risk_level") in ("low", "medium") else "medium",
            "risk_source": "offline_rule",
        })
        return result

    if _contains_keyword(text, conf.residentialKeywords):
        score = result.get("risk_score")
        result.update({
            "usage_type": "residential",
            "is_datacenter": False,
            "is_residential": True,
            "is_mobile": False,
            "risk_score": 20 if score in (None, "", 0, 50) else int(score),
            "risk_level": "low",
            "risk_source": "offline_rule",
        })
        return result

    result.update({
        "usage_type": "unknown",
        "risk_score": int(result.get("risk_score") or 50) or 50,
        "risk_level": "unknown",
        "risk_source": "offline_rule",
    })
    return result


@lru_cache(maxsize=conf.ipIntelCacheSize)
def lookup(ip):
    data = unknown_result(ip)
    if not ip or not conf.enableIpIntel:
        return data

    try:
        _init_readers()
        sources = []

        city_reader = _READERS.get("city")
        country_reader = _READERS.get("country")
        asn_reader = _READERS.get("asn")

        if city_reader:
            try:
                city = city_reader.city(ip)
                data["country_code"] = city.country.iso_code
                data["country_name"] = city.country.name
                subdivision = city.subdivisions.most_specific
                data["region_name"] = subdivision.name if subdivision else None
                data["city_name"] = city.city.name
                sources.append("maxmind_city")
            except Exception:
                pass

        if country_reader and not data.get("country_code"):
            try:
                country = country_reader.country(ip)
                data["country_code"] = country.country.iso_code
                data["country_name"] = country.country.name
                sources.append("maxmind_country")
            except Exception:
                pass

        if asn_reader:
            try:
                asn = asn_reader.asn(ip)
                data["asn"] = format_asn(asn.autonomous_system_number)
                data["asn_org"] = asn.autonomous_system_organization
                if not data.get("isp"):
                    data["isp"] = data["asn_org"]
                    sources.append("isp_fallback_asn_org")
                sources.append("maxmind_asn")
            except Exception:
                pass

        data["geo_source"] = ",".join(sources) if sources else "unknown"
        if conf.enableRiskRules:
            data = apply_risk_rules(data)
        return data
    except Exception as e:
        log.error("IP intelligence lookup failed for %s: %s" % (ip, str(e)))
        return unknown_result(ip)
