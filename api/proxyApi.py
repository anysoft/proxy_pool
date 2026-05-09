# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyApi.py
   Description :   WebApi
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/04: WebApi
                   2019/08/14: 集成Gunicorn启动方式
                   2020/06/23: 新增pop接口
                   2022/07/21: 更新count接口
-------------------------------------------------
"""
__author__ = 'JHao'

import platform
from random import choice
from html import escape
from werkzeug.wrappers import Response
from flask import Flask, jsonify, request

from util.six import iteritems
from helper.proxy import Proxy
from helper.ip_intel import status as geoip_status
from helper.proxy_filter import filter_proxies, has_filter
from helper.stats import asn_stats, country_stats, isp_stats, overview_stats
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler

app = Flask(__name__)
conf = ConfigHandler()
proxy_handler = ProxyHandler()


class JsonResponse(Response):
    @classmethod
    def force_type(cls, response, environ=None):
        if isinstance(response, (dict, list)):
            response = jsonify(response)

        return super(JsonResponse, cls).force_type(response, environ)


app.response_class = JsonResponse

api_list = [
    {"url": "/get", "params": "type: ''https'|''", "desc": "get a proxy"},
    {"url": "/pop", "params": "", "desc": "get and delete a proxy"},
    {"url": "/delete", "params": "proxy: 'e.g. 127.0.0.1:8080'", "desc": "delete an unable proxy"},
    {"url": "/all", "params": "type: ''https'|''", "desc": "get all proxy from proxy pool"},
    {"url": "/count", "params": "", "desc": "return proxy count"},
    {"url": "/stats/asns", "params": "", "desc": "return ASN stats"},
    {"url": "/stats/countries", "params": "", "desc": "return country stats"},
    {"url": "/stats/isps", "params": "", "desc": "return ISP stats"},
    {"url": "/stats/overview", "params": "", "desc": "return proxy pool overview"},
    {"url": "/stats/geoip", "params": "", "desc": "return local GeoIP database status"},
    {"url": "/admin/enrich", "params": "force: true|false", "desc": "backfill IP intelligence for stored proxies"},
    {"url": "/apis", "params": "", "desc": "browser friendly API list"}
    # 'refresh': 'refresh proxy pool',
]


@app.route('/')
def index():
    return {'url': api_list}


def _api_examples():
    return [
        "/get/",
        "/get/?type=https",
        "/get/?country_code=CN&usage_type=residential&max_risk_score=50",
        "/all/?country_code=JP&is_datacenter=false",
        "/all/?max_risk_score=50",
        "/stats/asns/",
        "/stats/countries/",
        "/stats/isps/",
        "/stats/overview/",
        "/stats/geoip/",
        "/admin/enrich/",
        "/admin/enrich/?force=true",
        "/count/",
    ]


@app.route('/apis')
@app.route('/apis/')
def apis():
    rows = []
    for item in api_list:
        url = escape(item["url"])
        params = escape(item.get("params") or "")
        desc = escape(item.get("desc") or "")
        rows.append('<tr><td><a href="{url}/">{url}</a></td><td>{params}</td><td>{desc}</td></tr>'.format(
            url=url, params=params, desc=desc))
    examples = ['<li><a href="{0}">{0}</a></li>'.format(escape(example)) for example in _api_examples()]
    html = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>ProxyPool APIs</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #222; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: left; }}
    th {{ background: #f6f8fa; }}
    code {{ background: #f6f8fa; padding: 2px 4px; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>ProxyPool API List</h1>
  <table>
    <thead><tr><th>API</th><th>Params</th><th>Description</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
  <h2>Examples</h2>
  <ul>{examples}</ul>
  <p>筛选参数支持 <code>country_code</code>, <code>asn</code>, <code>usage_type</code>, <code>risk_level</code>,
  <code>max_risk_score</code>, <code>is_datacenter</code>, <code>is_residential</code>, <code>is_mobile</code>,
  <code>is_proxy</code>, <code>is_vpn</code>, <code>source</code>, <code>anonymous</code> 等组合使用。</p>
</body>
</html>""".format(rows="".join(rows), examples="".join(examples))
    return Response(html, mimetype="text/html")


def _https_arg():
    return request.args.get("type", "").lower() == 'https'


def _filtered_proxies():
    return filter_proxies(proxy_handler.getAll(False), request.args)


@app.route('/get')
@app.route('/get/')
def get():
    if has_filter(request.args):
        proxies = _filtered_proxies()
        proxy = choice(proxies) if proxies else None
        return proxy.to_dict if proxy else {"code": 0, "src": "no proxy matched"}
    https = _https_arg()
    proxy = proxy_handler.get(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/pop')
@app.route('/pop/')
def pop():
    if has_filter(request.args):
        proxies = _filtered_proxies()
        proxy = choice(proxies) if proxies else None
        if proxy:
            proxy_handler.delete(proxy)
            return proxy.to_dict
        return {"code": 0, "src": "no proxy matched"}
    https = _https_arg()
    proxy = proxy_handler.pop(https)
    return proxy.to_dict if proxy else {"code": 0, "src": "no proxy"}


@app.route('/refresh/')
def refresh():
    # TODO refresh会有守护程序定时执行，由api直接调用性能较差，暂不使用
    return 'success'


@app.route('/all')
@app.route('/all/')
def getAll():
    if has_filter(request.args):
        proxies = _filtered_proxies()
    else:
        proxies = proxy_handler.getAll(_https_arg())
    return jsonify([_.to_dict for _ in proxies])


@app.route('/delete', methods=['GET'])
@app.route('/delete/', methods=['GET'])
def delete():
    proxy = request.args.get('proxy')
    status = proxy_handler.delete(Proxy(proxy))
    return {"code": 0, "src": status}


@app.route('/count')
@app.route('/count/')
def getCount():
    proxies = proxy_handler.getAll()
    http_type_dict = {}
    source_dict = {}
    for proxy in proxies:
        http_type = 'https' if proxy.https else 'http'
        http_type_dict[http_type] = http_type_dict.get(http_type, 0) + 1
        for source in proxy.source.split('/'):
            source_dict[source] = source_dict.get(source, 0) + 1
    return {"http_type": http_type_dict, "source": source_dict, "count": len(proxies)}


@app.route('/stats/asns')
@app.route('/stats/asns/')
def getAsnStats():
    return asn_stats(proxy_handler.getAll(False))


@app.route('/stats/countries')
@app.route('/stats/countries/')
def getCountryStats():
    return country_stats(proxy_handler.getAll(False))


@app.route('/stats/isps')
@app.route('/stats/isps/')
def getIspStats():
    return isp_stats(proxy_handler.getAll(False))


@app.route('/stats/overview')
@app.route('/stats/overview/')
def getOverviewStats():
    return overview_stats(proxy_handler.getAll(False))


@app.route('/stats/geoip')
@app.route('/stats/geoip/')
def getGeoipStatus():
    return geoip_status()


@app.route('/admin/enrich')
@app.route('/admin/enrich/')
def enrichAllProxies():
    force = request.args.get("force", "").lower() in ("true", "1", "yes")
    return proxy_handler.enrichAll(force=force)


def runFlask():
    if platform.system() == "Windows":
        app.run(host=conf.serverHost, port=conf.serverPort)
    else:
        import gunicorn.app.base

        class StandaloneApplication(gunicorn.app.base.BaseApplication):

            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super(StandaloneApplication, self).__init__()

            def load_config(self):
                _config = dict([(key, value) for key, value in iteritems(self.options)
                                if key in self.cfg.settings and value is not None])
                for key, value in iteritems(_config):
                    self.cfg.set(key.lower(), value)

            def load(self):
                return self.application

        _options = {
            'bind': '%s:%s' % (conf.serverHost, conf.serverPort),
            'workers': 4,
            'accesslog': '-',  # log to stdout
            'access_log_format': '%(h)s %(l)s %(t)s "%(r)s" %(s)s "%(a)s"'
        }
        StandaloneApplication(app, _options).run()


if __name__ == '__main__':
    runFlask()
