#!/usr/bin/env python3
# coding:utf-8

from base64 import b64encode
from json import loads
from urllib.parse import urlparse

import requests

TYPES = {
    "sina.it": "sinalt",
    "t.cn": "sina",
    "dwz.cn": "dwz",
    "qq.cn.hn": "qq.cn.hn",
    "tb.cn.hn": "tb.cn.hn",
    "jd.cn.hn": "jd.cn.hn",
    "tinyurl.com": "tinyurl",
    "qr.net": "qr",
    "goo.gl": "googl",
    "is.gd": "isgd",
    "j.mp": "jmp",
    "bit.ly": "bitly",
}


class SinaShortUrl():
    def __init__(self):
        self.cookies = requests.session().get('http://dwz.wailian.work/').cookies

    def generator(self, url, suffix=None):
        # 检查url是否输入了http://前缀
        scheme = urlparse(url).scheme
        if not scheme:
            url = 'http://' + url

        # base64编码用户输入的url
        url = b64encode(url.encode()).decode()
        # 确定用户需要的短链类型
        site = TYPES.get(suffix, "sina")
        # 拼接请求url
        requests_url = "http://dwz.wailian.work/api.php?url={url}&site={site}".format(url=url, site=site)

        # 构造header
        headers = {
            'host': "dwz.wailian.work",
            'connection': "keep-alive",
            'accept': "application/json, text/javascript, */*; q=0.01",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36",
            'referer': "http://dwz.wailian.work/",
            'accept-encoding': "gzip, deflate",
            'accept-language': "zh-CN,zh;q=0.8",
            'cache-control': "no-cache",
        }

        # 请求
        response = requests.request("GET", requests_url, headers=headers, cookies=self.cookies)

        # 结果判定
        if response.status_code == 200:
            result = loads(response.content)

            result_status = result['result']
            result_data = result['data']

            if not result_status.lower() == 'ok':
                print('未成功')
                print(response.content)
                return False

            return result_data


if __name__ == '__main__':
    test = SinaShortUrl()
    print(test.generator('xinxidawang.xyz/wo/long_url/1'))
