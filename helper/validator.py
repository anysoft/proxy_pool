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
from util.six import withMetaclass
from util.singleton import Singleton
from handler.configHandler import ConfigHandler

conf = ConfigHandler()

HEADER = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0',
          'Accept': '*/*',
          'Connection': 'keep-alive',
          'Accept-Language': 'zh-CN,zh;q=0.8'}

IP_REGEX = re.compile(r"(.*:.*@)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}")


class ProxyValidator(withMetaclass(Singleton)):
    pre_validator = []
    http_validator = []
    https_validator = []

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


@ProxyValidator.addPreValidator
def formatValidator(proxy):
    """检查代理格式"""
    return True if IP_REGEX.fullmatch(proxy) else False


@ProxyValidator.addHttpValidator
def httpTimeOutValidator(proxy):
    """ http检测超时 """

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        if r.status_code == 200:
            if conf.httpsUrlHeader and len(conf.httpsUrlHeader) > 0:
                for key in conf.httpsUrlHeader.keys():
                    if not r.headers.get(key) or not r.headers.get(key).startswith(conf.httpsUrlHeader.get(key)):
                        return False
                    return True
    except Exception as e:
        return False
    # try:
    #     r = head(conf.httpUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout)
    #     return True if r.status_code == 200 else False
    # except Exception as e:
    #     return False


@ProxyValidator.addHttpsValidator
def httpsTimeOutValidator(proxy):
    """https检测超时"""

    proxies = {"http": "http://{proxy}".format(proxy=proxy), "https": "https://{proxy}".format(proxy=proxy)}
    try:
        r = head(conf.httpsUrl, headers=HEADER, proxies=proxies, timeout=conf.verifyTimeout, verify=False)
        if r.status_code == 200:
            if conf.httpsUrlHeader and len(conf.httpsUrlHeader) > 0:
                for key in conf.httpsUrlHeader.keys():
                    if not r.headers.get(key) or not r.headers.get(key).startswith(conf.httpsUrlHeader.get(key)):
                        return False
                    return True
    except Exception as e:
        return False


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
#     httpsTimeOutValidator('222.240.52.33:7890')
