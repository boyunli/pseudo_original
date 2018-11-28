#coding:utf-8

import os
import random
import json
import time
import traceback

import requests
from fake_useragent import UserAgent

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def _crawl_proxy_ip():
    resp = requests.get('http://ubuntu.pydream.com:8000/?types=0&count=5&country=国内')
    socks = json.loads(resp.text)
    sock = random.choice(socks)
    return (sock[0], sock[1])

def get_ua():
    ua = UserAgent(verify_ssl=False)
    uar = ua.random
    print('UserAgent: {}'.format(uar))
    return uar

def rotate_headers(referer=None, origin=None, host=None, ua=None, charset=None):
    if not ua:
        ua = get_ua()
    headers = {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, sdch, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    if referer:
        headers['Referer'] = referer
    if origin:
        headers['Origin'] = origin
    if host:
        headers['Host'] = host
    if charset:
        headers["Content-Type"] = "charset={}".format(charset)
    return headers

def set_proxies():
    host, port = _crawl_proxy_ip()
    config = {
        "http": "http://{host}:{port}".format(host=host, port=port),
    }
    return host, config

def delete_no_use_proxy_ip(ip):
    requests.get('http://ubuntu.pydream.com:8000/delete?ip={ip}'.format(ip=ip))

def request_get(url, cookies=None, referer=None,
                origin=None, host=None, timeout=(3.05, 10), **kwargs):
    retry_count = 0
    ip = ''
    while True:
        try:
            ip, proxies = set_proxies()
            headers = rotate_headers(referer=referer, origin=origin, host=host)
            if cookies:
                res = requests.get(url, cookies=cookies,
                                   headers=headers,
                                   proxies=proxies,
                                   timeout=15,  verify=False, **kwargs)
            else:
                res = requests.get(url, headers=headers,
                                   proxies=proxies,
                                   timeout=15,  verify=False, **kwargs)
            return res
        except requests.exceptions.ProxyError:
            print('{flag} 代理无效 {flag}'.format(flag='-'*30))
            delete_no_use_proxy_ip(ip)
            retry_count += 1
            time.sleep(1)
            if retry_count == 5:
                return False
        except:
            traceback.print_exc()
            time.sleep(1)
            retry_count += 1
            if retry_count == 5:
                return False
