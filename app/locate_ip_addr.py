import requests
import re
from bs4 import BeautifulSoup


def check_ip_location(ipaddr):
    url = 'http://ip138.com/ips138.asp?ip=%s&action=2' % str(ipaddr)
    r = requests.get(url)
    html = BeautifulSoup(r.content.decode('gb2312'), 'lxml')

    try:
        ip_location = html.li.text.split('：')[1]
        return ip_location
    except BaseException:
        return None


def check_my_ip():
    url = 'http://1212.ip138.com/ic.asp'
    r = requests.get(url)
    r = r.content.decode('gb2312')
    return re.search('\d+\.\d+\.\d+\.\d+',r).group()


if __name__ == '__main__':
    print(check_my_ip())
