import requests
from bs4 import BeautifulSoup


def check_ip_location(ipaddr):
	url = 'http://ip138.com/ips138.asp?ip=%s&action=2'%str(ipaddr)
	r = requests.get(url)
	html = BeautifulSoup(r.content.decode('gb2312'),'lxml')

	try:
		ip_location =html.li.text.split('：')[1]
		return ip_location
	except:
		return None

