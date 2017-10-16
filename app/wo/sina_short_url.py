#!/usr/bin/env python3
# coding:utf-8
'''
新浪短链API
官方网站:http://dwz.wailian.work/

todo: 频率高了之后会触发滑动验证码.
'''

from base64 import b64encode
from json import loads
from urllib.parse import urlparse

import time
import hashlib
import requests
from urllib import parse
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

    def generator(self, url, suffix=None):
        '''官方生成短链的API,请求多了之后会出验证码~'''
        # 检查是否存在cookies,如无,则构造一个.
        if not self.cookies:
            self.cookies = requests.session().get('http://dwz.wailian.work/', timeout=20).cookies
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
            result_url = result['data'].get('short_url')

            if result_status.lower() == 'ok':
                return result_url

        print('未成功')
        print(response.content)
        return False

    @staticmethod
    def generator_mynb8(url):
        '''用于生成短链的第三方API,说明文档http://www.mynb8.com/wiki/sina.html'''
        APPKEY = '5414cc56366fa5089f0bb0778eca4024'
        LONG_URL = urlEncode(url)
        SIGN = md5Encode(APPKEY + md5Encode(LONG_URL))

        request_url = 'http://www.mynb8.com/api/sina?appkey={APPKEY}&sign={SIGN}&long_url={LONG_URL}'.format(
            APPKEY=APPKEY,
            LONG_URL=LONG_URL,
            SIGN=SIGN
        )

        r = requests.get(request_url, timeout=30)
        while r.text == "访问太频繁，两次访问最少相隔8秒":
            time.sleep(15)
            r = requests.get(request_url, timeout=30)

        if r.status_code == 200:
            try:
                result = loads(r.content)
                return result.get('data').get('short_url')
            except:
                return r.text


def md5Encode(str):
    m = hashlib.md5()
    m.update(str.encode())
    return m.hexdigest()


def urlEncode(str):
    '''用于转义, 注意下面这个safe,如果不设置的话就不会转义/这个符号'''
    return parse.quote(str.encode(), safe='')


def temp_apply_some_shorturl_to_database():
    '''往我的数据库里批量申请短链~~~~~~~~~~~~~~~~'''
    import pymysql

    connect = pymysql.Connect(
        host='192.168.0.98',
        port=3306,
        user='root',
        passwd='1123',
        db='flask-develop',
        charset="utf8"
    )
    cursor = connect.cursor()

    for i in range(54, 100):
        shorturl = SinaShortUrl.generator_mynb8('http://xinxidawang.xyz/wo/long_url/%s' % i)
        assert len(shorturl) == 19
        cursor.execute('INSERT INTO longurl VALUES("{}",{},"{}");'.format(i, "NULL", shorturl))
        connect.commit()
        time.sleep(10)

    cursor.close()
    connect.close()


if __name__ == '__main__':
    # temp_apply_some_shorturl_to_database()

    pass
