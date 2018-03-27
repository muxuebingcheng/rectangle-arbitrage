#!/usr/bin/python
# -*- coding:utf8 -*-
#standard packages
import sys
import logging
import redis
import os
from multiprocessing import Pool
import json
import time
from websocket import create_connection
import configparser

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
        key = currency_a + '-' + currency_b + '-amount'
        r.set(key,amount_pre)
        key = currency_a + '-' + currency_b + '-price'
        r.set(key,price_pre)


def main(conf_file_name):
    work_path = os.path.abspath(os.curdir)
    config_path = os.path.join(work_path, conf_file_name)
    conf = configparser.ConfigParser()
    conf.read(config_path)
    redis_ip=conf.get('conf', 'redis_ip')
    redis_port=conf.get('conf', 'redis_port')
    platform=conf.get('conf', 'platform')
    key=conf.get('conf', 'key')
    is_send_message=conf.get('conf', 'is_send_message')
    currency_list = json.loads(conf.get('conf', 'currency_list'))

    pool = redis.ConnectionPool(host=redis_ip, port=redis_port,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)
    ws = create_connection("ws://47.104.136.5:8201")

    #currency_list=['mtn','hsr']
    #currency_list = ['iost', 'elf']


    if ws.connected:
        # 链接成功 发送验证信息
        ws.send('{"action":"Authentication","key":"'+key+'"}',
                opcode=0x1)
        data_info = ws.recv()
        data_info_dict = json.loads(data_info)
        print(data_info_dict)

        # 精度信息
        ws.send('{"action":"GetSymbols","platform":"'+platform+'"}',
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
        for currency in currency_list:
            send_message_btc='{"action":"SubMarketDepth","symbol":"' +currency +'btc","platform":"'+platform+'"}'
            ws.send(send_message_btc)
            data_info=ws.recv()
            print(data_info)
            send_message_eth = '{"action":"SubMarketDepth","symbol":"' +currency+'eth","platform":"'+platform+'"}'
            ws.send(send_message_eth)
            data_info = ws.recv()
            print(data_info)
        time.sleep(10)
        p = Pool(len(currency_list))
        path = os.path.abspath(os.curdir) + '/data' + '/paths_result.dat'
        print(path)
        f = open(path, 'r')
        path_list = []
        for line in f.readlines():
            line = line.strip()
            a = json.loads(line)
            path_list.append(a)

        for x in currency_list:
            currency_path = (x, path_list,platform)
            p.apply_async(calc_core.calc_fork, args=(currency_path,))
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
                    if is_send_message =='no':
                        print('不发送')
                        continue
                    ws.send(result, opcode=0x1)
                    print("send message:"+result)
                else:
                    None

    else:
        print("认证失败")

if __name__ == "__main__":
    conf_file_name = sys.argv[1]
    main(conf_file_name)

