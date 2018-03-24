#!/usr/bin/python
# -*- coding:utf8 -*-

import unittest
import redis
import time

# currency_pair_info内容
    # data_info {u'symbol': u'hsr-eth',
    # u'bids': [[0.01105, 2.2376], [0.010981, 16.95], [0.010979, 34], [0.010978, 82.2761], [0.010972, 0.0007], [0.010936, 182.473], [0.010922, 86.7123]],
    # u'asks': [[0.011123, 34], [0.011124, 182.473], [0.01116, 34], [0.011168, 70.8], [0.011173, 56.52], [0.011253, 68], [0.011254, 88.9182]]}

def format_name(ori_name):
    return ori_name[:-3] + '-' + ori_name[-3:]

def format_currency_name(ori_name):
    return ori_name[:-3]

def gen_currency_pair_info(currency_pair_info_str,currency_pair_info,currency_list,r):

    # 货币信息redis结构 value是时间戳 超过一定时间认为过期
    # key:hsr-eth value:[timestamp]
    # key:hsr-btc value:[timestamp]
    # redis list结构 攒齐一对 向后方每个redis list(每个redis list 对应一个处理进程)
    if 'symbol' in currency_pair_info.keys():
        print("symbol")
    else:
        print("数据未到齐")
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
            # 填充price 和 number redis
            # /货币价格和数量redis结构
            # 买价结构 : key:hrs-etc_ask_price_1 value:0.011123
            # 买价结构 : key:hrs-etc_ask_number_1 value:34
            # 卖价结构 : key:hrs-etc_ask_price_1 value:0.01105
            # 卖价结构 : key:hrs-etc_bid_number_1 value:2.2376
            fill_price_number_to_redis(currency_pair_info,r)
            # 放队列
            put_redis_list(currency_pair_info_str,currency_pair_info,currency_list,r)

    # btc
    else:
        timestamp_now = time.time() * 1000
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
            # 填充price 和 number redis
            # /货币价格和数量redis结构
            # 买价结构 : key:hrs-etc_ask_price_1 value:0.011123
            # 买价结构 : key:hrs-etc_ask_number_1 value:34
            # 卖价结构 : key:hrs-etc_ask_price_1 value:0.01105
            # 卖价结构 : key:hrs-etc_bid_number_1 value:2.2376
            fill_price_number_to_redis(currency_pair_info,r)
            # 放队列
            put_redis_list(currency_pair_info_str,currency_pair_info,currency_list,r)

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
