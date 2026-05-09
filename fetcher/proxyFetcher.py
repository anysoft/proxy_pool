# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyFetcher
   Description :
   Author :        JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25: proxyFetcher
-------------------------------------------------
"""
__author__ = 'JHao'

import re
import json
from time import sleep

from util.webRequest import WebRequest


class ProxyFetcher(object):
    """
    proxy getter
    """

    @staticmethod
    def _proxy_format(ip, port):
        ip = str(ip or "").strip()
        port = str(port or "").strip()
        if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", ip) and port.isdigit():
            return "%s:%s" % (ip, port)
        return None

    @staticmethod
    def freeProxy01():
        """
        站大爷 https://www.zdaye.com/dayProxy.html
        """
        start_url = "https://www.zdaye.com/dayProxy.html"
        html_tree = WebRequest().get(start_url, verify=False).tree
        latest_page_time = html_tree.xpath("//span[@class='thread_time_info']/text()")[0].strip()
        from datetime import datetime
        interval = datetime.now() - datetime.strptime(latest_page_time, "%Y/%m/%d %H:%M:%S")
        if interval.seconds < 300:  # 只采集5分钟内的更新
            target_url = "https://www.zdaye.com/" + html_tree.xpath("//h3[@class='thread_title']/a/@href")[0].strip()
            while target_url:
                _tree = WebRequest().get(target_url, verify=False).tree
                for tr in _tree.xpath("//table//tr"):
                    ip = "".join(tr.xpath("./td[1]/text()")).strip()
                    port = "".join(tr.xpath("./td[2]/text()")).strip()
                    yield "%s:%s" % (ip, port)
                next_page = _tree.xpath("//div[@class='page']/a[@title='下一页']/@href")
                target_url = "https://www.zdaye.com/" + next_page[0].strip() if next_page else False
                sleep(5)

    @staticmethod
    def freeProxy02():
        """
        代理66 http://www.66ip.cn/
        """
        url = "http://www.66ip.cn/"
        resp = WebRequest().get(url, timeout=10).tree
        for i, tr in enumerate(resp.xpath("(//table)[3]//tr")):
            if i > 0:
                ip = "".join(tr.xpath("./td[1]/text()")).strip()
                port = "".join(tr.xpath("./td[2]/text()")).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy03():
        """ 开心代理 """
        target_urls = ["http://www.kxdaili.com/dailiip.html", "http://www.kxdaili.com/dailiip/2/1.html"]
        for url in target_urls:
            tree = WebRequest().get(url).tree
            for tr in tree.xpath("//table[@class='active']//tr")[1:]:
                ip = "".join(tr.xpath('./td[1]/text()')).strip()
                port = "".join(tr.xpath('./td[2]/text()')).strip()
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy04():
        """ FreeProxyList https://www.freeproxylists.net/zh/ """
        url = "https://www.freeproxylists.net/zh/?c=CN&pt=&pr=&a%5B%5D=0&a%5B%5D=1&a%5B%5D=2&u=50"
        tree = WebRequest().get(url, verify=False).tree
        from urllib import parse

        def parse_ip(input_str):
            html_str = parse.unquote(input_str)
            ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', html_str)
            return ips[0] if ips else None

        for tr in tree.xpath("//tr[@class='Odd']") + tree.xpath("//tr[@class='Even']"):
            ip = parse_ip("".join(tr.xpath('./td[1]/script/text()')).strip())
            port = "".join(tr.xpath('./td[2]/text()')).strip()
            if ip:
                yield "%s:%s" % (ip, port)

    @staticmethod
    def freeProxy05(page_count=1):
        """ 快代理 https://www.kuaidaili.com """
        url_pattern = [
            'https://www.kuaidaili.com/free/inha/{}/',
            'https://www.kuaidaili.com/free/intr/{}/'
        ]
        url_list = []
        for page_index in range(1, page_count + 1):
            for pattern in url_pattern:
                url_list.append(pattern.format(page_index))

        for url in url_list:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            sleep(1)  # 必须sleep 不然第二条请求不到数据
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxy06():
        """ 冰凌代理 https://www.binglx.cn """
        url = "https://www.binglx.cn/?page=1"
        try:
            tree = WebRequest().get(url).tree
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy07():
        """ 云代理 """
        urls = ['http://www.ip3366.net/free/?stype=1', "http://www.ip3366.net/free/?stype=2"]
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy08():
        """ 小幻代理 """
        urls = ['https://ip.ihuan.me/address/5Lit5Zu9.html']
        for url in urls:
            r = WebRequest().get(url, timeout=10)
            proxies = re.findall(r'>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</a></td><td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxy09(page_count=1):
        """ 免费代理库 """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?country=中国&page={}'.format(i)
            html_tree = WebRequest().get(url, verify=False).tree
            for index, tr in enumerate(html_tree.xpath("//table//tr")):
                if index == 0:
                    continue
                yield ":".join(tr.xpath("./td/text()")[0:2]).strip()

    @staticmethod
    def freeProxy10():
        """ 89免费代理 """
        r = WebRequest().get("https://www.89ip.cn/index_1.html", timeout=10)
        proxies = re.findall(
            r'<td.*?>[\s\S]*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})[\s\S]*?</td>[\s\S]*?<td.*?>[\s\S]*?(\d+)[\s\S]*?</td>',
            r.text)
        for proxy in proxies:
            yield ':'.join(proxy)

    @staticmethod
    def freeProxy11():
        """ 稻壳代理 https://www.docip.net/ """
        r = WebRequest().get("https://www.docip.net/data/free.json", timeout=10)
        try:
            for each in r.json['data']:
                yield each['ip']
        except Exception as e:
            print(e)

    @staticmethod
    def freeProxy12():
        """ Data5u http://www.data5u.com """
        r = WebRequest().get("http://www.data5u.com", timeout=10)
        for ul in r.tree.xpath("//ul[contains(@class, 'l2')]"):
            texts = [text.strip() for text in ul.xpath(".//span/text()") if text.strip()]
            if len(texts) >= 2:
                proxy = ProxyFetcher._proxy_format(texts[0], texts[1])
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy13():
        """ Fatezero http://proxylist.fatezero.org """
        r = WebRequest().get("http://proxylist.fatezero.org/proxy.list", timeout=10)
        for line in r.text.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                item = json.loads(line)
                proxy = ProxyFetcher._proxy_format(item.get("host"), item.get("port"))
                if proxy:
                    yield proxy
            except Exception:
                continue

    @staticmethod
    def freeProxy14(page_count=3):
        """ Geonode https://proxylist.geonode.com """
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://geonode.com",
            "Referer": "https://geonode.com/",
        }
        url = "https://proxylist.geonode.com/api/proxy-list?limit=500&page={}&sort_by=lastChecked&sort_type=desc"
        for page in range(1, page_count + 1):
            r = WebRequest().get(url.format(page), header=headers, timeout=10)
            try:
                for item in r.json.get("data", []):
                    protocols = [str(protocol).lower() for protocol in item.get("protocols", [])]
                    if protocols and "http" not in protocols and "https" not in protocols:
                        continue
                    proxy = ProxyFetcher._proxy_format(item.get("ip"), item.get("port"))
                    if proxy:
                        yield proxy
            except Exception:
                continue

    @staticmethod
    def freeProxy15():
        """ Goubanjia http://www.goubanjia.com """
        r = WebRequest().get("http://www.goubanjia.com/", timeout=10)
        for td in r.tree.xpath("//*[contains(@class, 'ip')]"):
            parts = []
            for child in td.xpath("./*"):
                style = child.attrib.get("style", "")
                if "none" in style:
                    continue
                text = "".join(child.xpath(".//text()")).strip()
                if text:
                    parts.append(text)
            ip_port = "".join(parts).strip()
            match = re.search(r"(\d{1,3}(?:\.\d{1,3}){3}):?(\d{2,5})$", ip_port)
            if match:
                proxy = ProxyFetcher._proxy_format(match.group(1), match.group(2))
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy16():
        """ IPHai http://www.iphai.com """
        r = WebRequest().get("http://www.iphai.com/", timeout=10)
        for tr in r.tree.xpath("//tr"):
            texts = [text.strip() for text in tr.xpath("./td/text()") if text.strip()]
            for index, text in enumerate(texts):
                if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", text) and index + 1 < len(texts):
                    proxy = ProxyFetcher._proxy_format(text, texts[index + 1])
                    if proxy:
                        yield proxy

    @staticmethod
    def freeProxy17():
        """ SEO方法 https://proxy.seofangfa.com """
        r = WebRequest().get("https://proxy.seofangfa.com/", timeout=10, verify=False)
        for tr in r.tree.xpath("//table[contains(@class, 'table')]//tr[position()>1]"):
            texts = [text.strip() for text in tr.xpath("./td/text()") if text.strip()]
            if len(texts) >= 2:
                proxy = ProxyFetcher._proxy_format(texts[0], texts[1])
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy18(page_count=3):
        """ 太阳代理 http://www.taiyanghttp.com/free/ """
        for page in range(1, page_count + 1):
            r = WebRequest().get("http://www.taiyanghttp.com/free/page{}".format(page), timeout=10)
            for item in r.tree.xpath("//*[contains(@class, 'tr') and contains(@class, 'ip_tr')]"):
                texts = [text.strip() for text in item.xpath("./div/text()") if text.strip()]
                if len(texts) >= 2:
                    proxy = ProxyFetcher._proxy_format(texts[0], texts[1])
                    if proxy:
                        yield proxy

    @staticmethod
    def freeProxy19():
        """ Uqidata https://ip.uqidata.com/free/index.html """
        def decode_port(input_str):
            nums = ["ABCDEFGHIZ".find(char) for char in input_str]
            if -1 in nums:
                return None
            return int("".join(str(num) for num in nums)) >> 3

        r = WebRequest().get("https://ip.uqidata.com/free/index.html", timeout=10, verify=False)
        for tr in r.tree.xpath("//*[@id='main_container']//table//tbody/tr[position()>2]"):
            ip_parts = []
            for node in tr.xpath(".//td[contains(@class, 'ip')]//*"):
                if "none" in node.attrib.get("style", ""):
                    continue
                text = "".join(node.xpath(".//text()")).strip()
                if text:
                    ip_parts.append(text)
            ip = "".join(ip_parts)
            port_class = " ".join(tr.xpath(".//td[contains(@class, 'port')]/@class"))
            classes = [item for item in port_class.split() if item != "port"]
            port = decode_port(classes[0]) if classes else None
            proxy = ProxyFetcher._proxy_format(ip, port)
            if proxy:
                yield proxy

    @staticmethod
    def freeProxy20(page_count=3):
        """ 小舒代理 http://www.xsdaili.cn """
        base_url = "http://www.xsdaili.cn/"
        r = WebRequest().get(base_url, timeout=10)
        links = r.tree.xpath("//a/@href")
        pages = []
        for link in links:
            match = re.search(r"/dayProxy/ip/(\d+)\.html", link)
            if match:
                pages.append(int(match.group(1)))
        if not pages:
            return
        latest_page = max(pages)
        for page in range(max(1, latest_page - page_count + 1), latest_page + 1):
            url = "http://www.xsdaili.cn/dayProxy/ip/{}.html".format(page)
            detail = WebRequest().get(url, timeout=10)
            for item in re.findall(r"(\d{1,3}(?:\.\d{1,3}){3}):(\d{2,5})", detail.text):
                proxy = ProxyFetcher._proxy_format(item[0], item[1])
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy21():
        """ 西刺代理 https://www.xicidaili.com """
        r = WebRequest().get("https://www.xicidaili.com/", timeout=10, verify=False)
        for tr in r.tree.xpath("//table[@id='ip_list']//tr"):
            texts = [text.strip() for text in tr.xpath("./td/text()") if text.strip()]
            if len(texts) >= 3:
                proxy = ProxyFetcher._proxy_format(texts[0], texts[1])
                if not proxy and len(texts) >= 4:
                    proxy = ProxyFetcher._proxy_format(texts[1], texts[2])
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy22():
        """ 西拉代理 http://www.xiladaili.com """
        r = WebRequest().get("http://www.xiladaili.com/", timeout=10)
        for ip_port in r.tree.xpath("//tbody/tr/td[1]/text()"):
            if ":" in ip_port:
                ip, port = ip_port.strip().split(":", 1)
                proxy = ProxyFetcher._proxy_format(ip, port)
                if proxy:
                    yield proxy

    @staticmethod
    def freeProxy23():
        """ 一切代理 http://ip.yqie.com/ipproxy.htm """
        r = WebRequest().get("http://ip.yqie.com/ipproxy.htm", timeout=10)
        for tr in r.tree.xpath("//*[@id='GridViewOrder']//tr[position()>1]"):
            texts = [text.strip() for text in tr.xpath("./td/text()") if text.strip()]
            if len(texts) >= 2:
                proxy = ProxyFetcher._proxy_format(texts[0], texts[1])
                if proxy:
                    yield proxy

    # @staticmethod
    # def wallProxy01():
    #     """
    #     PzzQz https://pzzqz.com/
    #     """
    #     from requests import Session
    #     from lxml import etree
    #     session = Session()
    #     try:
    #         index_resp = session.get("https://pzzqz.com/", timeout=20, verify=False).text
    #         x_csrf_token = re.findall('X-CSRFToken": "(.*?)"', index_resp)
    #         if x_csrf_token:
    #             data = {"http": "on", "ping": "3000", "country": "cn", "ports": ""}
    #             proxy_resp = session.post("https://pzzqz.com/", verify=False,
    #                                       headers={"X-CSRFToken": x_csrf_token[0]}, json=data).json()
    #             tree = etree.HTML(proxy_resp["proxy_html"])
    #             for tr in tree.xpath("//tr"):
    #                 ip = "".join(tr.xpath("./td[1]/text()"))
    #                 port = "".join(tr.xpath("./td[2]/text()"))
    #                 yield "%s:%s" % (ip, port)
    #     except Exception as e:
    #         print(e)

    # @staticmethod
    # def freeProxy10():
    #     """
    #     墙外网站 cn-proxy
    #     :return:
    #     """
    #     urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)

    # @staticmethod
    # def freeProxy11():
    #     """
    #     https://proxy-list.org/english/index.php
    #     :return:
    #     """
    #     urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
    #     request = WebRequest()
    #     import base64
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
    #         for proxy in proxies:
    #             yield base64.b64decode(proxy).decode()

    # @staticmethod
    # def freeProxy12():
    #     urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
    #     request = WebRequest()
    #     for url in urls:
    #         r = request.get(url, timeout=10)
    #         proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
    #         for proxy in proxies:
    #             yield ':'.join(proxy)


if __name__ == '__main__':
    p = ProxyFetcher()
    for _ in p.freeProxy06():
        print(_)

# http://nntime.com/proxy-list-01.htm
