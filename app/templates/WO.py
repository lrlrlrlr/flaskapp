import requests


def go(phonenum):
    url = "http://wotvnews.17wo.cn/wovideo/video/saveUser"
    headers = {
        'host': "wotvnews.17wo.cn",
        'connection': "keep-alive",
        'content-length': "66",
        'origin': "http://wotvnews.17wo.cn",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'x-requested-with': "XMLHttpRequest",
        'dnt': "1",
        'referer': "http://wotvnews.17wo.cn/wovideo/video/first?groupId=1494738826704&resourceId=31",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'cache-control': "no-cache",
    }

    data = 'param0=%s&param1=0&param2=31&param3=&param4=1494738826704' % phonenum
    response = requests.request("POST", url, headers=headers, data=data)
    print(response.text)


if __name__ == '__main__':
    i = 0
    with open(r'Z:\sms促活\hebin.txt') as file:
        for phonenum in file.readlines():
            i += 1
            if i < 5000:
                print(i,end='')
                go(phonenum.strip('\n'))
