#!/usr/bin/python
# -*- coding:utf8 -*-
#standard packages
import logging
import redis
import os
from multiprocessing import Pool
import json
import time
from websocket import create_connection

import socket

from calc import calc_core
from tools import generate_currency_pair_info


logging.basicConfig(level=logging.DEBUG,\
		format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',\
		datefmt='%m-%d %H:%M',\
		filename='log/debug.log',\
		filemode='a')


def fill_precision_info(precision_info_dict,r):
    for precision_info in precision_info_dict :
        currency_a=precision_info['base-currency']
        currency_b = precision_info['quote-currency']
        amount_pre=precision_info['amount-precision']
        price_pre = precision_info['price-precision']
        #hsr-eth sell
        #key:hsr-eth-sell value:2
        #key:hsr-eth-buy  value:8
        #hsr-btc buy
        #key:hsr-btc-sell value:3
        #key:hsr-btc-buy  value:7

        #key
        key = currency_a + '-' + currency_b + '-amount'
        r.set(key,amount_pre)
        key = currency_a + '-' + currency_b + '-price'
        r.set(key,price_pre)


def main():
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)
    ws = create_connection("ws://47.104.136.5:8201")

    #currency_list=['mtn','hsr']
    currency_list = ['trx','iost','hsr','wax','elf','itc','soc','dta','act','gnt','eth','blz','mtn','ht','zla','mds','nas','swftc','let','pay']

    if ws.connected:
        # 链接成功 发送验证信息
        ws.send('{"action":"Authentication","key":"02A3C2C6E4EF8FFB1A5DA176F9E8CC65"}',
                opcode=0x1)
        data_info = ws.recv()
        data_info_dict = json.loads(data_info)
        print(data_info_dict)

        # 精度信息
        ws.send('{"action":"GetSymbols","platform":"huobi"}',
                opcode=0x1)
        precision_info = ws.recv()
        precision_info_dict = json.loads(precision_info)
        print(precision_info_dict)
        precision_info_dict = precision_info_dict['symbols']
        fill_precision_info(precision_info_dict, r)
    else:
        # 连接失败
        print("failed")
        return
    # 校验验证信息
    if data_info_dict['msg'] == '认证成功':
        begin_timestamp = int(time.time())
        ws.send('{"action":"SubMarketDepth","symbol":"hsrbtc","platform":"huobi"}',
                opcode=0x1)
        #验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"hsreth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"mtnbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"mtneth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"iostbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"iosteth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"iostbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"waxeth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"waxbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)


        ws.send('{"action":"SubMarketDepth","symbol":"elfeth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"elfbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"payeth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"paybtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"leteth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"letbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"swftceth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"swftcbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"naseth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"nasbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"mdseth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"mdsbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"zlaeth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"zlabtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"hteth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"htbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"blzeth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"blzbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"gnteth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"gntbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"acteth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"actbtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"dtaeth","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"dtabtc","dtaform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"soceth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"socbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"trxeth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"trxbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"itceth","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        ws.send('{"action":"SubMarketDepth","symbol":"itcbtc","platform":"huobi"}',
                opcode=0x1)
        # 验证成功
        data_info = ws.recv()
        print(data_info)

        time.sleep(10)

        p = Pool(20)
        for x in currency_list:
            p.apply_async(calc_core.calc_fork, args=(x,))
        print('Waiting for all subprocesses done...')
        p.close()
        print('All subprocesses done.')
        pid = os.fork()
        if pid == 0:
            i_count=0
            while 1:
                data_info = ws.recv()
                i_count = i_count+1
                # print('-----------------------'+str(i_count)+'----'+str(time.time() * 1000))
                #收到变化的价格 灌入redis list
                if(data_info==None):
                    continue
                currency_pair_info_str=data_info
                currency_pair_info = json.loads(data_info)
                # print(currency_pair_info_str)
                generate_currency_pair_info.gen_currency_pair_info(currency_pair_info_str,currency_pair_info,currency_list,r);

        else:
            ws.send('{"type":"ping"}', opcode=0x1)
            while 1:
                end_timestamp = int(time.time())
                if (end_timestamp - begin_timestamp > 10):
                    ws.send('{"type":"ping"}', opcode=0x1)
                    begin_timestamp = end_timestamp
                    print("send heart beat")
                    time.sleep(1)
                result = r.lpop("list_result")
                if(result != None):
                    ws.send(result, opcode=0x1)
                    print("send message:"+result)
                else:
                    None

    else:
        print("认证失败")

if __name__ == "__main__":
    main()

