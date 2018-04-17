#!/usr/bin/python
# -*- coding:utf8 -*-
#standard packages
import sys
import redis
import os
from multiprocessing import Pool
import json
import time
from websocket import create_connection
import configparser
import tools.logger
import traceback
import signal


from calc import calc_core
from tools import generate_currency_pair_info



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


def main_process(r,key,platform,currency_list,is_send_message,logger,redis_ip,redis_port):
    #redis-cli -h 127.0.0.1 -p 6380 keys "*" | xargs redis-cli -h 127.0.0.1 -p 6380 del
    command = ' redis-cli -h '+ str(redis_ip) + ' -p ' + str(redis_port) + ' keys "*" | xargs redis-cli -h ' + str(redis_ip) + ' -p ' + str(redis_port) + ' del '
    logger.info(command)
    os.system(command)

    ws = create_connection("ws://47.104.136.5:8201")
    if ws.connected:
        # 链接成功 发送验证信息
        ws.send('{"action":"Authentication","key":"' + key + '"}',
                opcode=0x1)
        data_info = ws.recv()
        data_info_dict = json.loads(data_info)
        logger.info(data_info_dict)
        # 精度信息
        precision_request='{"action":"GetSymbols","platform":"' + platform + '"}'
        logger.info(precision_request)
        ws.send(precision_request,
                opcode=0x1)
        precision_info = ws.recv()
        precision_info_dict = json.loads(precision_info)
        logger.info(precision_info_dict)
        precision_info_dict = precision_info_dict['symbols']
        fill_precision_info(precision_info_dict, r)
    else:
        # 连接失败
        logger.info("failed")
        return
    # 校验验证信息
    if data_info_dict['msg'] == '认证成功':
        begin_timestamp = int(time.time())
        for currency in currency_list:
            send_message_btc = '{"action":"SubMarketDepth","symbol":"' + currency + 'btc","platform":"' + platform + '"}'
            print(send_message_btc)
            ws.send(send_message_btc)
            data_info = ws.recv()
            logger.info(data_info)
            send_message_eth = '{"action":"SubMarketDepth","symbol":"' + currency + 'eth","platform":"' + platform + '"}'
            print(send_message_eth)
            ws.send(send_message_eth)
            data_info = ws.recv()
            logger.info(data_info)
        time.sleep(10)

        pid = os.fork()
        if pid == 0:
            i_count = 0
            while 1:
                data_info = ws.recv()
                i_count = i_count + 1
                # print('-----------------------'+str(i_count)+'----'+str(time.time() * 1000))
                # 收到变化的价格 灌入redis list
                if (data_info == None):
                    continue
                currency_pair_info_str = data_info
                #print(currency_pair_info_str)
                currency_pair_info = json.loads(data_info)
                generate_currency_pair_info.gen_currency_pair_info(currency_pair_info_str, currency_pair_info,
                                                                   currency_list, r);

        else:
            pplogger = tools.logger.Logger('ppid', str(pid)+'ppid.log')
            ws.send('{"type":"ping"}', opcode=0x1)
            try:
                while 1:
                    end_timestamp = int(time.time())
                    if (end_timestamp - begin_timestamp > 8):
                        try:
                            ws.send('{"type":"ping"}', opcode=0x1)
                            begin_timestamp = end_timestamp
                            pplogger.info('send heart beat')
                        except Exception as e:
                            pplogger.info('error son pid')
                            pplogger.info(str(e))
                            msg = traceback.format_exc()
                            pplogger.info(msg)
                            pplogger.info('子进程pid:'+str(pid))
                            time.sleep(100)
                            #command = 'kill -9 '+ str(pid)
                            #os.system(command)
                    result = r.lpop("list_result")
                    if (result != None):
                        if is_send_message == 'no':
                            pplogger.info('不发送')
                            continue
                        ws.send(result, opcode=0x1)
                        pplogger.info('send message:' + result)
                    else:
                        None
            except Exception as e:
                pplogger.info('子进程异常信息')
                pplogger.info(str(e))
                msg = traceback.format_exc()
                pplogger.info(msg)

    else:
        logger.info('认证失败')


def main(conf_file_name):
    pid = os.getpid()
    logger = tools.logger.Logger('mainlog', str(pid)+'main.log')
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
    recalc_num = conf.get('conf','recalc_num')

    pool = redis.ConnectionPool(host=redis_ip, port=redis_port,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)

    #启动货币处理进程池
    p = Pool(len(currency_list))
    path = os.path.abspath(os.curdir) + '/data' + '/paths_result.dat'
    logger.info(path)
    f = open(path, 'r')
    path_list = []
    for line in f.readlines():
        line = line.strip()
        a = json.loads(line)
        path_list.append(a)
    f.close()

    limit_info_file = os.path.abspath(os.curdir) + '/data' + '/limit.dat'
    f = open(limit_info_file, 'r')
    limit_info = f.readline()
    f.close()
    limit_info_json = json.loads(limit_info)

    for x in currency_list:
        currency_path = (x, path_list, platform,redis_ip,redis_port,limit_info_json)
        p.apply_async(calc_core.calc_fork, args=(currency_path,))
    logger.info('Waiting for all subprocesses done...')
    p.close()
    logger.info('All subprocesses done.')

    #recalc process pool
    p_recalc = Pool(int(recalc_num))
    for i in range(int(recalc_num)):
        p_recalc.apply_async(calc_core.recalc, args=((redis_ip,redis_port,platform,limit_info_json),))

    while 1:
        try:
            main_process(r,key,platform,currency_list,is_send_message,logger,redis_ip,redis_port)
        except Exception as e:
            logger.info(e)
            msg = traceback.format_exc()
            logger.info(msg)
        time.sleep(15)

if __name__ == "__main__":
    conf_file_name = sys.argv[1]
    main(conf_file_name)

