#!/usr/bin/env python3
#-*- coding:'utf-8' -*-
'''
用途: 刷UV,不带GUI
'''
import requests
import time
import multiprocessing


def do(url,delay=0):
    url='http://w.17wo.cn/'+str(url)#拼接短链
    r=requests.get(url,timeout=10,allow_redirects=False)
    time.sleep(delay)
    return r.status_code


class counter():
    def __init__(self,name):
        self.name=str(name)
        self.count=0

    def callback(self,result):
        self.count+=1
        print('count:{} url:{} statuscode:{}'.format(self.count,self.name,result))


def main(urllist,n,delay=0):
    pool=multiprocessing.Pool(2)
    print('任务开始')
    for tempurl in urllist:
        c=counter(tempurl)
        for i in range(n):
            pool.apply_async(func=do,args=(tempurl,delay,),callback=c.callback)
    pool.close()
    pool.join()
    print('all done! success_num:',c.count)


def uvweaver_async(app,urllist,n,delay=0):#异步发送邮件
    with app.app_context():
        main(urllist,n,delay=0)


def main_async(urllist,n,delay=0):
    from flask import current_app
    from threading import Thread
    app=current_app._get_current_object()
    thr=Thread(target=uvweaver_async,args=(app,urllist,n,delay,))
    thr.start()
    return thr


if __name__=='__main__':
    # # 地址
    # urllist=['eEvuYjF','3UVNz26']
    # # 任务量
    # n=2
    # # 延时
    # delay=0.1
    list=['QzA3iib','N7jquyu','aEZJFjv','EJVJbya','fQ3A3iE']

    main(list,10000)
