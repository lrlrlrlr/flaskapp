import datetime
import os

import requests


class shorturl_platform():
    def __init__(self):
        print('login.. plz wait!')
        url="http://w.17wo.cn/shortUrl/login.do"
        self.username=os.environ.get('SHORTURL_PLATFORM_USERNAME')
        self.password=os.environ.get('SHORTURL_PLATFORM_PASSWORD')

        headers={
            'host':"w.17wo.cn",
            'connection':"keep-alive",
            'content-length':"35",
            'cache-control':"no-cache",
            'origin':"http://w.17wo.cn",
            'upgrade-insecure-requests':"1",
            'user-agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/59.0.3071.115 Safari/537.36",
            'content-type':"application/x-www-form-urlencoded",
            'accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'referer':"http://w.17wo.cn/shortUrl/loginOut",
            'accept-encoding':"gzip, deflate",
            'accept-language':"zh-CN,zh;q=0.8",
            'cookie':"SESSION=e0370062-1ce3-4821-b72e-11258a0e0bf1",
        }

        data='username={}&password={}'.format(self.username,self.password)
        response=requests.request("POST",url,headers=headers,data=data)
        self.cookies=response.cookies
        print('Login success!')

    def check_shorturl_data(self,shortUrl,starttime=None,endtime=None):
        if starttime is None and endtime is None:
            starttime=datetime.datetime.strftime(
                datetime.datetime.now()-datetime.timedelta(7),'%Y%m%d')
            endtime=datetime.datetime.strftime(
                datetime.datetime.now(),'%Y%m%d')

        url="http://w.17wo.cn/shortUrl/realTimeStatisList"

        headers={
            'host':"w.17wo.cn",
            'connection':"keep-alive",
            'accept':"application/json, text/javascript, */*; q=0.01",
            'origin':"http://w.17wo.cn",
            'x-requested-with':"XMLHttpRequest",
            'user-agent':"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/59.0.3071.115 Safari/537.36",
            'content-type':"application/x-www-form-urlencoded; charset=UTF-8",
            'referer':"http://w.17wo.cn/shortUrl/chartReport",
            'accept-encoding':"gzip, deflate",
            'accept-language':"zh-CN,zh;q=0.8",
            'cache-control':"no-cache",
        }

        data='dateBegin=%s&dateEnd=%s&taskId=&shortUrl=%s'%(
            starttime,endtime,shortUrl)

        response=requests.post(
            url,
            headers=headers,
            cookies=self.cookies,
            data=data)
        r=response.json()

        keys=[
            'taskId',
            'taskName',
            'channelName',
            'shortUrl',
            'statisDate',
            'pv',
            'uv']
        for stat in r['property']['realTimeVisitStatisList']:
            for key in keys:
                print(stat[key],end='  ')
            print()


#todo 这里要把print改成return

if __name__=='__main__':
    t=shorturl_platform()
    lst=['rUvIrmu','EjuU3q6','3ENjAb6','BBjuqyq','7rY7B3b','zaArAjB','6f673im','MB3Mfqb','zENrquI','feA73qQ']

    for i in lst:
        t.check_shorturl_data(i,'20170831','20170904')
