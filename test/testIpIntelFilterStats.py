# -*- coding: utf-8 -*-
"""
Simple regression tests for IP intelligence, filtering and stats helpers.
Run with: python3 test/testIpIntelFilterStats.py
"""
from __future__ import absolute_import

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from helper.ip_intel import lookup
from helper.proxy import Proxy
from helper.proxy_filter import filter_proxies, parse_bool
from helper.stats import asn_stats, country_stats, isp_stats


def test_old_proxy_json_compat():
    raw = json.dumps({
        "proxy": "118.190.79.36:8090",
        "https": False,
        "fail_count": 0,
        "region": "广东省深圳市",
        "anonymous": "",
        "source": "freeProxy14",
        "check_count": 4,
        "last_status": True,
        "last_time": "2021-05-26 10:58:04",
    })
    proxy = Proxy.createFromJson(raw)
    assert proxy.ip == "118.190.79.36"
    assert proxy.port == 8090
    assert proxy.country_code is None
    assert proxy.usage_type == "unknown"
    assert proxy.risk_score == 0
    assert proxy.is_datacenter is False
    assert proxy.to_dict["country_code"] is None


def test_asn_and_bool_filter_compat():
    proxy = Proxy("1.2.3.4:8080", asn="AS4134", country_code="CN", is_datacenter=False)
    assert filter_proxies([proxy], {"asn": "4134"}) == [proxy]
    assert filter_proxies([proxy], {"asn": "AS4134"}) == [proxy]
    assert parse_bool("true") is True
    assert parse_bool("false") is False
    assert parse_bool("1") is True
    assert parse_bool("0") is False
    assert parse_bool("yes") is True
    assert parse_bool("no") is False


def test_combined_filter():
    cn = Proxy("1.2.3.4:8080", https=False, country_code="CN", country_name="China",
               asn="4134", asn_org="CHINANET-BACKBONE", isp="China Telecom",
               usage_type="residential", risk_score=20, risk_level="low",
               is_residential=True, anonymous="anonymous", source="unit")
    jp = Proxy("5.6.7.8:8080", https=False, country_code="JP", country_name="Japan",
               asn="2516", asn_org="KDDI", isp="KDDI",
               usage_type="mobile", risk_score=30, risk_level="medium",
               is_mobile=True, anonymous="elite", source="unit")
    matched = filter_proxies([cn, jp], {
        "country_code": "cn",
        "usage_type": "Residential",
        "max_risk_score": "50",
        "is_residential": "1",
        "asn_org": "chinanet",
        "anonymous": "anonymous",
    })
    assert matched == [cn]
    assert filter_proxies([cn, jp], {"country_code": "US"}) == []


def test_lookup_without_mmdb_returns_unknown():
    data = lookup("203.0.113.1")
    assert data["usage_type"] == "unknown"
    assert data["risk_level"] == "unknown"
    assert data["is_residential"] is False


def test_stats_helpers():
    proxies = [
        Proxy("1.2.3.4:8080", country_code="CN", country_name="China",
              asn="4134", asn_org="CHINANET-BACKBONE", isp="China Telecom",
              usage_type="residential"),
        Proxy("1.2.3.5:8080", country_code="CN", country_name="China",
              asn="4134", asn_org="CHINANET-BACKBONE", isp="China Telecom",
              usage_type="residential"),
        Proxy("5.6.7.8:8080", country_code="JP", country_name="Japan",
              asn="2516", asn_org="KDDI", isp="KDDI", usage_type="mobile"),
    ]
    asns = asn_stats(proxies)
    countries = country_stats(proxies)
    isps = isp_stats(proxies)
    assert asns["count"] == 2
    assert asns["items"][0]["asn"] == "AS4134"
    assert asns["items"][0]["count"] == 2
    assert countries["count"] == 2
    assert countries["items"][0]["country_code"] == "CN"
    assert isps["count"] == 2
    assert isps["items"][0]["isp"] == "China Telecom"
    assert isps["items"][0]["asns"] == ["AS4134"]


if __name__ == '__main__':
    test_old_proxy_json_compat()
    test_asn_and_bool_filter_compat()
    test_combined_filter()
    test_lookup_without_mmdb_returns_unknown()
    test_stats_helpers()
    print("IP intel/filter/stats tests ok!")
