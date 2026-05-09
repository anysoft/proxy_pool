# -*- coding: utf-8 -*-
"""
Proxy filtering helpers for API query parameters.
"""
from __future__ import absolute_import

from helper.proxy import format_asn


FILTER_KEYS = (
    "type", "country_code", "country", "asn", "asn_org", "isp", "usage_type",
    "risk_level", "max_risk_score", "is_datacenter", "is_residential",
    "is_mobile", "is_proxy", "is_vpn", "source", "anonymous"
)


def has_filter(args):
    return any(args.get(key) not in (None, "") for key in FILTER_KEYS)


def parse_bool(value):
    if value is None or value == "":
        return None
    value = str(value).strip().lower()
    if value in ("true", "1", "yes"):
        return True
    if value in ("false", "0", "no"):
        return False
    return None


def _text_contains(value, expected):
    if expected in (None, ""):
        return True
    return str(expected).lower() in str(value or "").lower()


def _text_equal(value, expected):
    if expected in (None, ""):
        return True
    return str(value or "").lower() == str(expected).lower()


def _asn_equal(value, expected):
    if expected in (None, ""):
        return True
    return format_asn(value) == format_asn(expected)


def match_proxy(proxy, args):
    if _text_equal(args.get("type"), "https") and not proxy.https:
        return False
    if _text_equal(args.get("type"), "http") and proxy.https:
        return False
    if not _text_equal(proxy.country_code, args.get("country_code")):
        return False
    if not _text_equal(proxy.country_name, args.get("country")):
        return False
    if not _asn_equal(proxy.asn, args.get("asn")):
        return False
    if not _text_contains(proxy.asn_org, args.get("asn_org")):
        return False
    if not _text_contains(proxy.isp, args.get("isp")):
        return False
    if not _text_equal(proxy.usage_type, args.get("usage_type")):
        return False
    if not _text_equal(proxy.risk_level, args.get("risk_level")):
        return False
    if not _text_contains(proxy.source, args.get("source")):
        return False
    if not _text_equal(proxy.anonymous, args.get("anonymous")):
        return False

    max_risk_score = args.get("max_risk_score")
    if max_risk_score not in (None, ""):
        try:
            if int(proxy.risk_score or 0) > int(max_risk_score):
                return False
        except ValueError:
            return False

    for field in ("is_datacenter", "is_residential", "is_mobile", "is_proxy", "is_vpn"):
        expected = parse_bool(args.get(field))
        if expected is not None and bool(getattr(proxy, field)) != expected:
            return False
    return True


def filter_proxies(proxies, args):
    return [proxy for proxy in proxies if match_proxy(proxy, args)]
