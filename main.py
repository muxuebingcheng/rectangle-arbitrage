#!/usr/bin/python
# -*- coding:utf8 -*-
#standard packages
import logging
import redis
import os,time
from multiprocessing import Pool
import json
import time
#log config
from calc import calc_core
from tools import generate_currency_pair_info

logging.basicConfig(level=logging.DEBUG,\
		format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
		datefmt='%m-%d %H:%M',\
		filename='log/debug.log',\
		filemode='a')

if __name__ == "__main__":
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)
    # 启动多进程处理函数
    p = Pool(4)
    for x in ['mtn', 'hsr']:
        p.apply_async(calc_core.calc_fork,args=(x,))

    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')

    while True:
        # ws.recv()接受信息处理
        time.sleep(1)
        currency_info_str = ""
        currency_info_str = r.lpop("source")
        if (currency_info_str == None):
            print("数据空")
            continue
        currency_info_dict = json.loads(currency_info_str)
        generate_currency_pair_info.gen_currency_pair_info(currency_info_dict, r)

