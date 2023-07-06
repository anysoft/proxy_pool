# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     proxyScheduler
   Description :
   Author :        JHao
   date：          2019/8/5
-------------------------------------------------
   Change Activity:
                   2019/08/05: proxyScheduler
                   2021/02/23: runProxyCheck时,剩余代理少于POOL_SIZE_MIN时执行抓取
-------------------------------------------------
"""
__author__ = 'JHao'

import threading

from apscheduler.executors.pool import ThreadPoolExecutor

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ProcessPoolExecutor

from util.six import Queue
from helper.fetch import Fetcher
from helper.check import Checker
from handler.logHandler import LogHandler
from handler.proxyHandler import ProxyHandler
from handler.configHandler import ConfigHandler


def __runProxyFetch():
    proxy_queue = Queue()
    proxy_fetcher = Fetcher()

    for proxy in proxy_fetcher.run():
        proxy_queue.put(proxy)

    Checker("raw", proxy_queue)


def __runProxyCheck_raw():
    proxy_handler = ProxyHandler()
    if proxy_handler.db.getCount().get("total", 0) < proxy_handler.conf.poolSizeMin:
        __runProxyFetch()

def __runProxyCheck_use():
    proxy_handler = ProxyHandler()
    proxy_queue = Queue()
    for proxy in proxy_handler.getAll():
        proxy_queue.put(proxy)
    Checker("use", proxy_queue)


def runScheduler():
    config_handler = ConfigHandler()
    timezone = config_handler.timezone
    proxy_fetch_interval = config_handler.proxyFetchInterval
    proxy_check_interval = config_handler.proxyCheckInterval

    scheduler_log = LogHandler("scheduler")

    __runProxyCheck_use()
    scheduler_check = BlockingScheduler(logger=scheduler_log, timezone=timezone)
    scheduler_check.add_job(__runProxyCheck_use, 'interval', minutes=proxy_check_interval, id="proxy_check_use", name="proxy检查_use")
    scheduler_check.add_executor(ThreadPoolExecutor(max_workers=5))

    scheduler_thread = threading.Thread(target=scheduler_check.start)
    scheduler_thread.start()

    __runProxyFetch()
    scheduler_fetch = BlockingScheduler(logger=scheduler_log, timezone=timezone)
    scheduler_fetch.add_job(__runProxyFetch, 'interval', minutes=proxy_fetch_interval, id="proxy_fetch", name="proxy采集")
    scheduler_fetch.add_job(__runProxyCheck_raw, 'interval', minutes=proxy_check_interval, id="proxy_check_raw", name="proxy检查_raw")
    executors = {
        'default': {'type': 'threadpool', 'max_workers': 20},
        'processpool': ProcessPoolExecutor(max_workers=5)
    }
    job_defaults = {
        'coalesce': False,
        'max_instances': 10
    }
    scheduler_fetch.configure(executors=executors, job_defaults=job_defaults, timezone=timezone)
    scheduler_fetch.start()





# if __name__ == '__main__':
#     runScheduler()
