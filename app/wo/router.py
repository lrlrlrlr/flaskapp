import requests, time
from selenium.webdriver.common.keys import Keys


class router():
    '''监控本地路由器'''

    def __init__(self):
        self.url = 'http://192.168.0.1/'
        pass

    def initial(self):
        s = requests.session()
        r = s.get(self.url)
        assert r.status_code == 200

    def selenium_login(self):
        from selenium import webdriver
        driver = webdriver.Chrome(r'D:\DDL DATA\OneDrive\tools\chromedriver.exe')
        driver.get(self.url)
        time.sleep(5)  # todo 这里换成等待
        psw_element = driver.find_element_by_xpath('//*[@id="lgPwd"]')
        psw_element.send_keys('17071707')
        psw_element.send_keys(Keys.RETURN)
