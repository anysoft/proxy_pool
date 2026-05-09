# -*- coding: utf-8 -*-
"""
-------------------------------------------------
   File Name：     setting.py
   Description :   配置文件
   Author :        JHao
   date：          2019/2/15
-------------------------------------------------
   Change Activity:
                   2019/2/15:
-------------------------------------------------
"""

BANNER = r"""
****************************************************************
*** ______  ********************* ______ *********** _  ********
*** | ___ \_ ******************** | ___ \ ********* | | ********
*** | |_/ / \__ __   __  _ __   _ | |_/ /___ * ___  | | ********
*** |  __/|  _// _ \ \ \/ /| | | ||  __// _ \ / _ \ | | ********
*** | |   | | | (_) | >  < \ |_| || |  | (_) | (_) || |___  ****
*** \_|   |_|  \___/ /_/\_\ \__  |\_|   \___/ \___/ \_____/ ****
****                       __ / /                          *****
************************* /___ / *******************************
*************************       ********************************
****************************************************************
"""

VERSION = "2.4.0"

# ############### server config ###############
HOST = "0.0.0.0"

PORT = 5010

# ############### database config ###################
# db connection uri
# example:
#      Redis: redis://:password@ip:port/db
#      Ssdb:  ssdb://:password@ip:port
DB_CONN = 'redis://:pwd@127.0.0.1:6379/0'

# proxy table name
TABLE_NAME = 'use_proxy'


# ###### config the proxy fetch function ######
PROXY_FETCHER = [
    "freeProxy01",
    #"freeProxy02",
    "freeProxy03",
    "freeProxy04",
    "freeProxy05",
    #"freeProxy06",
    "freeProxy07",
    "freeProxy08",
    "freeProxy09",
    "freeProxy10",
    "freeProxy11",
    "freeProxy14",
    "freeProxy15",
    "freeProxy16",
    #"freeProxy17",
    "freeProxy18",
    "freeProxy19",
    "freeProxy20",
    "freeProxy21",
    "freeProxy22"
    #"freeProxy23"
]

# ############# proxy validator #################
# 代理验证目标网站
HTTP_URL = "http://httpbin.org"

HTTPS_URL = "https://www.qq.com"

# 代理验证时超时时间
VERIFY_TIMEOUT = 10

# 近PROXY_CHECK_COUNT次校验中允许的最大失败次数,超过则剔除代理
MAX_FAIL_COUNT = 0

# 近PROXY_CHECK_COUNT次校验中允许的最大失败率,超过则剔除代理
# MAX_FAIL_RATE = 0.1

# proxyCheck时代理数量少于POOL_SIZE_MIN触发抓取
POOL_SIZE_MIN = 20

# ############# concurrency #################
# 每个代理源内部仍单线程抓取，多个代理源之间并行抓取。
FETCH_SCHEDULER_WORKERS = 20

# 代理校验线程数，适当提高可以加快入库和复检速度。
PROXY_CHECKER_THREAD_COUNT = 50

# ############# proxy attributes #################
# 是否启用代理地域属性
PROXY_REGION = True

# 是否启用离线 IP 画像识别。数据库文件不存在时不会影响代理池运行。
ENABLE_IP_INTEL = True
ENABLE_ONLINE_IP_LOOKUP = False
GEOIP_COUNTRY_DB = "./data/geoip/GeoLite2-Country.mmdb"
GEOIP_CITY_DB = "./data/geoip/GeoLite2-City.mmdb"
GEOIP_ASN_DB = "./data/geoip/GeoLite2-ASN.mmdb"
IP_INTEL_CACHE_SIZE = 10000

ENABLE_RISK_RULES = True

DATACENTER_KEYWORDS = [
    "amazon", "aws", "google", "gcp", "microsoft", "azure", "alibaba", "aliyun",
    "tencent", "huawei", "oracle", "digitalocean", "vultr", "linode",
    "ovh", "hetzner", "contabo", "leaseweb", "choopa", "host", "hosting",
    "cloud", "data center", "datacenter", "server", "colo", "colocation"
]

MOBILE_KEYWORDS = [
    "mobile", "cellular", "wireless", "kcell", "vodafone", "orange",
    "docomo", "softbank", "au", "kddi", "china mobile"
]

RESIDENTIAL_KEYWORDS = [
    "telecom", "chinanet", "china unicom", "china mobile", "ntt",
    "kddi", "softbank", "comcast", "verizon", "att", "bt", "sky",
    "telefonica", "deutsche telekom"
]

# 预留在线查询配置，本项目默认不依赖在线服务。
IPINFO_TOKEN = ""
IPQUALITYSCORE_TOKEN = ""

# ############# scheduler config #################

# Set the timezone for the scheduler forcely (optional)
# If it is running on a VM, and
#   "ValueError: Timezone offset does not match system offset"
#   was raised during scheduling.
# Please uncomment the following line and set a timezone for the scheduler.
# Otherwise it will detect the timezone from the system automatically.

TIMEZONE = "Asia/Shanghai"
