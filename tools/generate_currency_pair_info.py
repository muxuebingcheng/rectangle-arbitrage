#!/usr/bin/python
# -*- coding:utf8 -*-

import unittest
import time
import traceback
import os
from calc import calc_core
import json
import tools.logger
import redis

def format_name(ori_name):
    return ori_name[:-3] + '-' + ori_name[-3:]

def format_currency_name(ori_name):
    return ori_name[:-3]

def gen_currency_pair_info(logger,currency_pair_info_str,currency_pair_info,currency_list,r,recalc_num_limit,redis_ip_redis_port_platform_limit):

    try:
        if 'action' in currency_pair_info.keys():
            print(1,currency_pair_info_str, 1)
            action = currency_pair_info['action']
            if action == 'RbackPath':
                print(currency_pair_info_str, 2)
                # 获取多少进程正在计算
                try:
                    recalc_info_json = json.loads(currency_pair_info_str)
                    currency_a = recalc_info_json['path'][0]['from']
                    currency_b = recalc_info_json['path'][3]['from']
                    step_1_status = recalc_info_json['path'][0]['status']
                    step_2_status = recalc_info_json['path'][1]['status']
                    step_3_status = recalc_info_json['path'][2]['status']
                    step_4_status = recalc_info_json['path'][3]['status']
                    uniq_id = recalc_info_json['uniqid']
                    step = 0
                    if int(step_2_status) == 1:
                        step = 2
                        x_begin = recalc_info_json['path'][0]['xbegin']
                    elif int(step_3_status) == 1:
                        step = 3
                        x_begin = recalc_info_json['path'][0]['xbegin']
                        y_middle = recalc_info_json['path'][2]['ymiddle']
                    else:
                        logger.info("重算消息格式错误:" + currency_pair_info_str)
                        return
                except Exception as e:
                    msg = traceback.format_exc()
                    logger(msg)
                    return
                # recalc_process_list_status对次队列进行cao操作 hset : recalc_process_list pid status
                list_len = r.llen("recalc_process_list")
                # 默认没有空闲
                free_process_flag = False

                # 是否是停止消息
                #找是否需要替换
                for i in range(list_len):
                    #查看哪个进程空闲
                    ppid_in_list = r.lindex("recalc_process_list",i)
                    status = r.hget("recalc_process_list_status",str(ppid_in_list))
                    #如果有个进程的正在计算的uniq_id 和 传入的一致 则替换
                    if status == uniq_id:
                        #如果进程空闲 将计算信息传入 子进程每次计算后 判断一下当前计算的uniq 是否和传入的一致
                        r.set("recalc_data_"+ppid_in_list,currency_pair_info_str)
                        logger.info("替换计算的进程:"+str(ppid_in_list))
                        logger.info("替换计算的数据uniq_id:" + str(uniq_id))
                        #替换成功后返回
                        return

                #找空闲进程
                for i in range(list_len):
                    #查看哪个进程空闲
                    ppid_in_list = r.lindex("recalc_process_list",i)
                    status = r.hget("recalc_process_list_status",str(ppid_in_list))
                    if status == "none":
                        #如果进程空闲 将计算信息传入 子进程每次计算后 判断一下当前计算的uniq 是否和传入的一致
                        r.set("recalc_data_"+ppid_in_list,currency_pair_info_str)
                        r.hset("recalc_process_list_status", str(ppid_in_list),uniq_id)
                        free_process_flag = True
                        logger.info("找到空闲的进程:" + str(ppid_in_list))
                        logger.info("空闲的进程的数据:" + currency_pair_info_str)
                        return

                #没有空闲进程 挑出一个正在计算的 换成这个
                if free_process_flag == False:
                    index = list_len-1
                    ppid_in_list = r.lindex("recalc_process_list",index)
                    r.set("recalc_data_" + ppid_in_list, currency_pair_info_str)
                    r.hset("recalc_process_list_status", str(ppid_in_list),uniq_id)
                    logger.info("替换进程id:" + str(ppid_in_list))
                    logger.info("替换进程的数据:" + currency_pair_info_str)
                    # logger.info("睡一秒")
                    # time.sleep(1)
                    #设置这个进程的计算进行为新的
                return
            #停止计算
            elif action == 'stopPath':
                # 找是否需要替换
                list_len = r.llen("recalc_process_list")
                uniq_id_stop = currency_pair_info["uniqid"]
                for i in range(list_len):
                    # 查看哪个进程空闲
                    ppid_in_list = r.lindex("recalc_process_list", i)
                    status = r.hget("recalc_process_list_status", str(ppid_in_list))
                    if status == uniq_id_stop:
                        r.hset("recalc_process_list_status", str(ppid_in_list), "none")
                        logger.info("停止计算的进程:" + str(ppid_in_list))
                        logger.info("停止计算的进程的uniq_id:" + uniq_id_stop)
                        return
                logger("未找到停止计算进程:" + uniq_id_stop)
                return

    except Exception as e:
        msg = traceback.format_exc()
        print(msg)


    #填充事实信息货币
    if 'symbol' in currency_pair_info.keys():
        a=1
    else:
        #print("数据未到齐")
        return
    currency_pair_name = format_name(currency_pair_info['symbol'])
    # 装载redis数据
    currency_pair_name_list = currency_pair_name.split('-');
    if currency_pair_name_list[1] == 'eth':
        timestamp_now = int(round(time.time() * 1000))
        # 先找配对的btc
        key = currency_pair_name_list[0] + '-' + 'btc'
        r.set(currency_pair_name, timestamp_now)

        #for test
        r.set(key, timestamp_now)
        if r.get(key)=='':
            return
        else:
            timestamp_redis = int(r.get(key))

        if (timestamp_now - timestamp_redis > 1000):
            # 对应货币对信息过期
            r.delete(key)
        else:
            # 只需要填充
            fill_price_number_to_redis(currency_pair_info,r)

    # btc
    else:
        timestamp_now = int(round(time.time() * 1000))
        # 先找配对的eth
        key = currency_pair_name_list[0] + '-' + 'eth'
        r.set(currency_pair_name, timestamp_now)
        timestamp_redis = r.get(key)
        if timestamp_redis==None:
            timestamp_redis = timestamp_now
        if (timestamp_now - int(timestamp_redis) > 1000):
            # 对应货币对信息过期
            r.delete(key)
        else:
            #只需要填充
            fill_price_number_to_redis(currency_pair_info,r)

    # currency_pair_info_str=r.get("yangxi")
    # currency_pair_info = json.loads(currency_pair_info_str

    return


def fill_price_number_to_redis(currency_info,r):
    # currency_data内容
    # data_info {u'symbol': u'hsr-eth',
    # u'bids': [[0.01105, 2.2376], [0.010981, 16.95], [0.010979, 34], [0.010978, 82.2761], [0.010972, 0.0007], [0.010936, 182.473], [0.010922, 86.7123]],
    # u'asks': [[0.011123, 34], [0.011124, 182.473], [0.01116, 34], [0.011168, 70.8], [0.011173, 56.52], [0.011253, 68], [0.011254, 88.9182]]}

    # 货币价格和数量redis结构
    # 买价结构 : key1:hrs-etc_ask_price_1 value:0.011123
    # 买价结构 : key2:hrs-etc_ask_number_1 value:34
    # 卖价结构 : key3:hrs-etc_ask_price_1 value:0.01105
    # 卖价结构 : key4:hrs-etc_bid_number_1 value:2.2376
    ask_list = currency_info['asks']
    bid_list = currency_info['bids']
    keydict = {}

    #asks
    currency_info['symbol'] = currency_info['symbol'][:-3]+'-'+currency_info['symbol'][-3:]

    ask_price_key_0 = currency_info['symbol'] + '_ask_price_0'
    ask_price_value_0 = ask_list[0][0]
    ask_num_key_0 = currency_info['symbol'] + '_ask_num_0'
    ask_num_value_0 = ask_list[0][1]

    keydict[ask_price_key_0] = ask_price_value_0
    keydict[ask_num_key_0] = ask_num_value_0

    ask_price_key_1 = currency_info['symbol'] + '_ask_price_1'
    ask_price_value_1 = ask_list[1][0]
    ask_num_key_1 = currency_info['symbol'] + '_ask_num_1'
    ask_num_value_1 = ask_list[1][1]

    keydict[ask_price_key_1] = ask_price_value_1
    keydict[ask_num_key_1] = ask_num_value_1

    ask_price_key_2 = currency_info['symbol'] + "_ask_price_2"
    ask_price_value_2 = ask_list[2][0]
    ask_num_key_2 = currency_info['symbol'] + "_ask_num_2"
    ask_num_value_2 = ask_list[2][1]

    keydict[ask_price_key_2] = ask_price_value_2
    keydict[ask_num_key_2] = ask_num_value_2

    ask_price_key_3 = currency_info['symbol'] + "_ask_price_3"
    ask_price_value_3 = ask_list[3][0]
    ask_num_key_3 = currency_info['symbol'] + "_ask_num_3"
    ask_num_value_3 = ask_list[3][1]

    keydict[ask_price_key_3] = ask_price_value_3
    keydict[ask_num_key_3] = ask_num_value_3

    ask_price_key_4 = currency_info['symbol'] + "_ask_price_4"
    ask_price_value_4 = ask_list[4][0]
    ask_num_key_4 = currency_info['symbol'] + "_ask_num_4"
    ask_num_value_4 = ask_list[4][1]

    keydict[ask_price_key_4] = ask_price_value_4
    keydict[ask_num_key_4] = ask_num_value_4

    # bids
    bid_price_key_0 = currency_info['symbol'] + '_bid_price_0'
    bid_price_value_0 = bid_list[0][0]
    bid_num_key_0 = currency_info['symbol'] + '_bid_num_0'
    bid_num_value_0 = bid_list[0][1]

    keydict[bid_price_key_0] = bid_price_value_0
    keydict[bid_num_key_0] = bid_num_value_0

    bid_price_key_1 = currency_info['symbol'] + '_bid_price_1'
    bid_price_value_1 = bid_list[1][0]
    bid_num_key_1 = currency_info['symbol'] + '_bid_num_1'
    bid_num_value_1 = bid_list[1][1]

    keydict[bid_price_key_1] = bid_price_value_1
    keydict[bid_num_key_1] = bid_num_value_1

    bid_price_key_2 = currency_info['symbol'] + "_bid_price_2"
    bid_price_value_2 = bid_list[2][0]
    bid_num_key_2 = currency_info['symbol'] + "_bid_num_2"
    bid_num_value_2 = bid_list[2][1]

    keydict[bid_price_key_2] = bid_price_value_2
    keydict[bid_num_key_2] = bid_num_value_2

    bid_price_key_3 = currency_info['symbol'] + "_bid_price_3"
    bid_price_value_3 = bid_list[3][0]
    bid_num_key_3 = currency_info['symbol'] + "_bid_num_3"
    bid_num_value_3 = bid_list[3][1]

    keydict[bid_price_key_3] = bid_price_value_3
    keydict[bid_num_key_3] = bid_num_value_3

    bid_price_key_4 = currency_info['symbol'] + "_bid_price_4"
    bid_price_value_4 = bid_list[4][0]
    bid_num_key_4 = currency_info['symbol'] + "_bid_num_4"
    bid_num_value_4 = bid_list[4][1]

    keydict[bid_price_key_4] = bid_price_value_4
    keydict[bid_num_key_4] = bid_num_value_4
    r.mset(keydict)

    return

def put_redis_list(currency_pair_info_str,currency_pair_info,currency_list,r):
    for currency in currency_list:
            format_name = format_currency_name(currency_pair_info['symbol'])
            if format_name != currency:
                r.lpush("list_"+currency,currency_pair_info_str)

if __name__ == '__main__':
    unittest.main()
