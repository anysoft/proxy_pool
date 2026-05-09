# -*- coding: utf-8 -*-
"""
Aggregation helpers for proxy pool statistics.
"""
from __future__ import absolute_import


def _sorted_items(counter):
    return sorted(counter.items(), key=lambda item: (-item[1], str(item[0] or "")))


def asn_stats(proxies):
    buckets = {}
    for proxy in proxies:
        asn = proxy.asn or "unknown"
        item = buckets.setdefault(asn, {
            "asn": asn,
            "asn_org": proxy.asn_org,
            "count": 0,
            "countries": set(),
            "usage_types": set(),
        })
        item["count"] += 1
        if proxy.asn_org and not item.get("asn_org"):
            item["asn_org"] = proxy.asn_org
        if proxy.country_code:
            item["countries"].add(proxy.country_code)
        if proxy.usage_type:
            item["usage_types"].add(proxy.usage_type)
    items = []
    for item in buckets.values():
        item["countries"] = sorted(item["countries"])
        item["usage_types"] = sorted(item["usage_types"])
        items.append(item)
    items.sort(key=lambda item: (-item["count"], item["asn"]))
    return {"count": len(items), "items": items}


def country_stats(proxies):
    buckets = {}
    for proxy in proxies:
        code = proxy.country_code or "unknown"
        item = buckets.setdefault(code, {
            "country_code": code,
            "country_name": proxy.country_name,
            "count": 0,
        })
        item["count"] += 1
        if proxy.country_name and not item.get("country_name"):
            item["country_name"] = proxy.country_name
    items = sorted(buckets.values(), key=lambda item: (-item["count"], item["country_code"]))
    return {"count": len(items), "items": items}


def isp_stats(proxies):
    buckets = {}
    for proxy in proxies:
        isp = proxy.isp or "unknown"
        item = buckets.setdefault(isp, {
            "isp": isp,
            "count": 0,
            "countries": set(),
            "asns": set(),
        })
        item["count"] += 1
        if proxy.country_code:
            item["countries"].add(proxy.country_code)
        if proxy.asn:
            item["asns"].add(proxy.asn)
    items = []
    for item in buckets.values():
        item["countries"] = sorted(item["countries"])
        item["asns"] = sorted(item["asns"])
        items.append(item)
    items.sort(key=lambda item: (-item["count"], item["isp"]))
    return {"count": len(items), "items": items}


def overview_stats(proxies):
    by_country = {}
    by_asn = {}
    by_isp = {}
    by_usage_type = {}
    by_risk_level = {}

    for proxy in proxies:
        by_country[proxy.country_code or "unknown"] = by_country.get(proxy.country_code or "unknown", 0) + 1
        by_asn[proxy.asn or "unknown"] = by_asn.get(proxy.asn or "unknown", 0) + 1
        by_isp[proxy.isp or "unknown"] = by_isp.get(proxy.isp or "unknown", 0) + 1
        by_usage_type[proxy.usage_type or "unknown"] = by_usage_type.get(proxy.usage_type or "unknown", 0) + 1
        by_risk_level[proxy.risk_level or "unknown"] = by_risk_level.get(proxy.risk_level or "unknown", 0) + 1

    return {
        "total": len(proxies),
        "by_country": dict(_sorted_items(by_country)),
        "by_asn": dict(_sorted_items(by_asn)),
        "by_isp": dict(_sorted_items(by_isp)),
        "by_usage_type": dict(_sorted_items(by_usage_type)),
        "by_risk_level": dict(_sorted_items(by_risk_level)),
        "datacenter_count": len([proxy for proxy in proxies if proxy.is_datacenter]),
        "residential_count": len([proxy for proxy in proxies if proxy.is_residential]),
        "mobile_count": len([proxy for proxy in proxies if proxy.is_mobile]),
        "proxy_count": len([proxy for proxy in proxies if proxy.is_proxy]),
        "vpn_count": len([proxy for proxy in proxies if proxy.is_vpn]),
    }
