# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     _validators
   Description :   定义proxy验证方法
   Author :        JHao
   date：          2021/5/25
-------------------------------------------------
   Change Activity:
                   2023/03/10: 支持带用户认证的代理格式 username:password@ip:port
-------------------------------------------------
"""
__author__ = 'JHao'

import re
from requests import head
from requests import get
from urllib3.exceptions import ConnectTimeoutError

from handler.logHandler import LogHandler
from helper.proxy import Proxy, ProxyType
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler
from requests.exceptions import ProxyError, ConnectTimeout

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")

log = LogHandler("checker")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []
    socks5_validator = []

    @classmethod
    def addPreValidator(cls, func):
        cls.pre_validator.append(func)
        return func

    @classmethod
    def addHttpValidator(cls, func):
        cls.http_validator.append(func)
        return func

    @classmethod
    def addHttpsValidator(cls, func):
        cls.https_validator.append(func)
        return func

    @classmethod
    def addSocks5Validator(cls, func):
        cls.socks5_validator.append(func)
        return func


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy, proxyType=ProxyType.HTTP.value):
    """ 标准可用性检测 """
    proxies = {"http": "{protocol}://{proxy}".format(proxy=proxy, protocol=proxyType),
               "https": "{protocol}://{proxy}".format(proxy=proxy, protocol=proxyType)}
    try:
        r = get(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=(conf.connectTimeout, conf.readTimeout), verify=False)
        # log.info(str(proxy) + str(r.headers) + r.text)
        if r.status_code == 200:
            # headers check
            if conf.httpsUrlHeader and len(conf.httpsUrlHeader) > 0:
                for key in conf.httpsUrlHeader.keys():
                    if not r.headers.get(key) or not r.headers.get(key).startswith(conf.httpsUrlHeader.get(key)):
                        return False
            # bodys check
            if conf.httpsUrlBody and len(conf.httpsUrlBody) > 0:
                json_bject = conf.httpsUrlBody.get('json')
                body_array = conf.httpsUrlBody.get('strings')
                # check body json
                if json_bject and len(json_bject) > 0:
                    if r.text.startswith('{') and r.text.endswith('}'):
                        for key in json_bject.keys():
                            if not r.text or not r.text.__contains__(json_bject.get(key)) or not r.text.__contains__(key):
                                return False
                # check body contain strings
                if body_array and len(body_array) > 0:
                    for key in body_array:
                        if not r.text or not r.text.__contains__(key):
                            return False

            return True
    except (ProxyError, ConnectTimeout, ConnectTimeoutError) as e:
        if str(e).__contains__('Cannot connect to proxy') \
                or str(e).__contains__('Unable to connect to proxy') \
                or str(e).__contains__('timed out') \
                or str(e).__contains__('ConnectTimeoutError'):
            raise e
        log.info(e)
        return False
    except ConnectTimeoutError as e:
        raise e
    except Exception as e:
        # log.info(e)
        raise e
    return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy, proxyType=ProxyType.HTTPS.value):
    return httpTimeOutValidator(proxy, proxyType=proxyType)


@ProxyValidator.addSocks5Validator
def socks5TimeOutValidator(proxy, proxyType=ProxyType.HTTPS.value):
    """ socks5 检测超时"""
    return httpTimeOutValidator(proxy, proxyType=proxyType)


@ProxyValidator.addHttpValidator
def customValidatorExample(proxy):
    """自定义validator函数，校验代理是否可用, 返回True/False"""
    return True
    # # 使用cloudflare 作为认证，确保server 正常(部分代理地址已经变成了web站导致单纯head status验证不足)
    # proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    # try:
    #     r = head('https://1.1.1.1', headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
    #     return True if r.status_code == 200 and r.headers.get('server') == 'cloudflare' else False
    # except Exception as e:
    #     return False

# if __name__ == '__main__':
#     print(httpsTimeOutValidator('106.75.247.75:8889'))
#     print(httpTimeOutValidator('106.75.247.75:8889'))
#     print(socks5TimeOutValidator('106.75.247.75:8889'))
