#!/usr/bin/python
# -*- coding:utf8 -*-
import os
from multiprocessing import Pool
import json
import redis
import tools.logger
import traceback
import time


def string_to_float_list(string_list):
    for i in range(20):
        string_list[i] = float(string_list[i])
    return string_list

#def calc_fork(currency_b,path_list):
def calc_fork(currency_path_platform_redis_ip_redis_port):
    # pool = redis.ConnectionPool(host='127.0.0.1', port=6379,
    #                             decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    # r = redis.Redis(connection_pool=pool)
    ppid = os.getpid()
    logger = tools.logger.Logger(str(ppid) + 'pplog', currency_path_platform_redis_ip_redis_port[0]+str(ppid) + '.log')
    r=redis.Redis(host=currency_path_platform_redis_ip_redis_port[3], port=currency_path_platform_redis_ip_redis_port[4])
    #print("计算货币:"+currency_path_platform[0])
    #获取路径
    redis_list_key = 'list_'+currency_path_platform_redis_ip_redis_port[0]
    # path_info = generate_path_info.get_paths_from_local_data('/Users/yangxi/projectpython/rectangle-arbitrage/data/paths_ordered.dat')
    # path_info = [[0, 1], [0, 1], [0, 1], [0, 1]]
    # print(path_info)
    timestamp_last = int(time.time())
    timestamp_now = int(time.time())
    last_ratio = 0
    while 1:
        #print("redis_list_key:"+redis_list_key)
        currency_info_str = r.lpop(redis_list_key)
        if (currency_info_str == None):
            #print("数据空fork")
            continue
        #print("redis_list_key:" + redis_list_key)
        currency_info_str = currency_info_str.decode()
        currency_info_dict = json.loads(currency_info_str)
        currency_a=currency_info_dict['symbol']
        currency_a=currency_a[:-3]
        timestamp_now = int(time.time())
        if timestamp_now - timestamp_last > 10 :
            timestamp_last = timestamp_now
            last_ratio = 0
        try:
            last_ratio=calc_profit(r,currency_a,currency_path_platform_redis_ip_redis_port[0],currency_path_platform_redis_ip_redis_port[1],currency_path_platform_redis_ip_redis_port[2],logger,last_ratio)
        except Exception as e:
            logger.info(str(e))
            msg = traceback.format_exc()
            logger.info(msg)


def calc_profit(r, currency_a, currency_b, path_list, platform, logger, last_ratio):
    #currency_name = mtn
    #os.pid
    pid =str(os.getpid())
    if currency_a == currency_b:
        return 0
    #检查货币信息
    log_info_list=[]
    #print('pid: ' +pid+ '++'+currency_a+'----------'+currency_b)
    log_info_list.append('pid: ' +pid+ ' : '+currency_a+'-------------------------------------------'+currency_b)
    if r.get(currency_b  + '-'+ 'btc') == '':
        return 0
    if r.get(currency_b + '-' + 'eth') == '':
        return 0
    #货币信息存在 计算x起和a
    #获取路径
    # 先算[[0],[0],[0],[0]]
    # 再算其他[[0,1],[0,1],[0,1,2],[0,1,2,3]]
    #get_path()
    path_info_list=[]
    #从redis list中获取要计算的货币（FIFO） hrs a
    #批量获取两种货币(hrs mtn)和eth btc的价格
    # 货币价格和数量redis结构
    # 买价结构 : key1:hrs-etc_ask_price_1 value:0.011123
    # 买价结构 : key2:hrs-etc_ask_num_1 value:34

    # 卖价结构 : key3:hrs-etc_bid_price_1 value:0.01105
    # 卖价结构 : key4:hrs-etc_bid_num_1 value:2.2376

    # hrs的价格 x a
    key_pre = currency_a + '-' + 'eth'
    test_null = r.get(key_pre + '_ask_price_0')
    if(test_null == None):
        return 0
    currency_x_a_list =[
        key_pre + '_ask_price_0', key_pre + '_ask_num_0', #0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1', #2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2', #4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3', #6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4', #8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0', #10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1', #12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2', #14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3', #16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  #18 19
    ]

    currency_x_a_info_list = r.mget(currency_x_a_list)
    currency_x_a_info_list=string_to_float_list(currency_x_a_info_list)

    str_print=""
    ii = 1;
    for elem in currency_x_a_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii+1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_a + '-eth-'+str_print)
    #print('pid: ' + pid + '--' + currency_a + '-eth-'+str_print)

    str_print = ""

    # mtn的价格 x b
    key_pre = currency_b + '-' + 'eth'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 0
    currency_x_b_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_x_b_info_list = r.mget(currency_x_b_list)
    currency_x_b_info_list = string_to_float_list(currency_x_b_info_list)

    str_print = ""
    for elem in currency_x_b_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_b + '-eth-' + str_print)
    #print('pid: ' + pid + '--' + currency_b + '-eth-' + str_print)

    str_print = ""
    # 前20是mtn价格和数量 后20是hrs价格和数量

    #btc对应信息
    #hrs y a
    key_pre = currency_a + '-' + 'btc'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 0
    currency_y_a_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_y_a_info_list = r.mget(currency_y_a_list)
    currency_y_a_info_list = string_to_float_list(currency_y_a_info_list)

    str_print = ""
    for elem in currency_y_a_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_a + '-btc-' + str_print)
    #print('pid: ' + pid + '--' + currency_a + '-btc-' + str_print)

    str_print = ""

    # mtn的价格 y b
    key_pre = currency_b + '-' + 'btc'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 0
    currency_y_b_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_y_b_info_list = r.mget(currency_y_b_list)
    currency_y_b_info_list = string_to_float_list(currency_y_b_info_list)


    for elem in currency_y_b_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_b + '-btc-' + str_print)
    #print('pid: ' + pid + '--' + currency_b + '-btc-' + str_print)




    x_a_bids_price = [0] * 5
    x_a_bids_num = [0] * 5
    x_a_bids_price[0] = currency_x_a_info_list[10] #price
    x_a_bids_num[0] = 0.01*currency_x_a_info_list[11]   #num
    x_a_bids_price[1] = currency_x_a_info_list[12]
    x_a_bids_num[1] = 0.02*currency_x_a_info_list[13]
    x_a_bids_price[2] = currency_x_a_info_list[14]
    x_a_bids_num[2] = 0.03*currency_x_a_info_list[15]
    x_a_bids_price[3] = currency_x_a_info_list[16]
    x_a_bids_num[3] = 0.04*currency_x_a_info_list[17]
    x_a_bids_price[4] = currency_x_a_info_list[18]
    x_a_bids_num[4] = 0.05*currency_x_a_info_list[19]

    y_a_asks_price = [0] * 5
    y_a_asks_num = [0] * 5
    y_a_asks_price[0] = currency_y_a_info_list[0] #price
    y_a_asks_num[0] = 0.01*currency_y_a_info_list[1]   #num
    y_a_asks_price[1] = currency_y_a_info_list[2]
    y_a_asks_num[1] = 0.02*currency_y_a_info_list[3]
    y_a_asks_price[2] = currency_y_a_info_list[4]
    y_a_asks_num[2] = 0.03*currency_y_a_info_list[5]
    y_a_asks_price[3] = currency_y_a_info_list[6]
    y_a_asks_num[3] = 0.04*currency_y_a_info_list[7]
    y_a_asks_price[4] = currency_y_a_info_list[8]
    y_a_asks_num[4] = 0.05*currency_y_a_info_list[9]

    y_a_bids_price = [0] * 5
    y_a_bids_num = [0] * 5
    y_a_bids_price[0] = currency_y_a_info_list[10] #price
    y_a_bids_num[0] = 0.01*currency_y_a_info_list[11]   #num
    y_a_bids_price[1] = currency_y_a_info_list[12]
    y_a_bids_num[1] = 0.02*currency_y_a_info_list[13]
    y_a_bids_price[2] = currency_y_a_info_list[14]
    y_a_bids_num[2] = 0.03*currency_y_a_info_list[15]
    y_a_bids_price[3] = currency_y_a_info_list[16]
    y_a_bids_num[3] = 0.04*currency_y_a_info_list[17]
    y_a_bids_price[4] = currency_y_a_info_list[18]
    y_a_bids_num[4] = 0.05*currency_y_a_info_list[19]

    if (y_a_bids_price[0] - y_a_bids_price[1]) / y_a_bids_price[0] > 0.015 or (y_a_bids_price[1] - y_a_bids_price[2]) / y_a_bids_price[1] > 0.015 or (y_a_bids_price[2] - y_a_bids_price[3]) / y_a_bids_price[2] > 0.015 or (y_a_bids_price[3] - y_a_bids_price[4]) / y_a_bids_price[3] > 0.015 :
        return 0

    x_a_asks_price = [0] * 5
    x_a_asks_num = [0] * 5
    x_a_asks_price[0] = currency_x_a_info_list[0]
    x_a_asks_num[0] = 0.01*currency_x_a_info_list[1]
    x_a_asks_price[1] = currency_x_a_info_list[2]
    x_a_asks_num[1] = 0.02*currency_x_a_info_list[3]
    x_a_asks_price[2] = currency_x_a_info_list[4]
    x_a_asks_num[2] = 0.03*currency_x_a_info_list[5]
    x_a_asks_price[3] = currency_x_a_info_list[6]
    x_a_asks_num[3] = 0.04*currency_x_a_info_list[7]
    x_a_asks_price[4] = currency_x_a_info_list[8]
    x_a_asks_num[4] = 0.05*currency_x_a_info_list[9]

    if (x_a_asks_price[1] - x_a_asks_price[0]) / x_a_asks_price[0] > 0.015 or (x_a_asks_price[2] - x_a_asks_price[1]) / x_a_asks_price[1] > 0.015 or (x_a_asks_price[3] - x_a_asks_price[2]) / x_a_asks_price[2] > 0.015 or (x_a_asks_price[4] - x_a_asks_price[3]) / x_a_asks_price[3] > 0.015 :
        return 0

    x_b_bids_price = [0] * 5
    x_b_bids_num = [0] * 5
    x_b_bids_price[0] = currency_x_b_info_list[10]
    x_b_bids_num[0] = 0.01*currency_x_b_info_list[11]
    x_b_bids_price[1] = currency_x_b_info_list[12]
    x_b_bids_num[1] = 0.02*currency_x_b_info_list[13]
    x_b_bids_price[2] = currency_x_b_info_list[14]
    x_b_bids_num[2] = 0.03*currency_x_b_info_list[15]
    x_b_bids_price[3] = currency_x_b_info_list[16]
    x_b_bids_num[3] = 0.04*currency_x_b_info_list[17]
    x_b_bids_price[4] = currency_x_b_info_list[18]
    x_b_bids_num[4] = 0.05*currency_x_b_info_list[19]

    if (x_b_bids_price[0] - x_b_bids_price[1]) / x_b_bids_price[0] > 0.015 or (x_b_bids_price[1] - x_b_bids_price[2]) / x_b_bids_price[1] > 0.015 or (x_b_bids_price[2] - x_b_bids_price[3]) / x_b_bids_price[2] > 0.015 or (x_b_bids_price[3] - x_b_bids_price[4]) / x_b_bids_price[3] > 0.015 :
        return 0

    y_b_asks_price = [0] * 5
    y_b_asks_num = [0] * 5
    y_b_asks_price[0] = currency_y_b_info_list[0]
    y_b_asks_num[0] = 0.01*currency_y_b_info_list[1]
    y_b_asks_price[1] = currency_y_b_info_list[2]
    y_b_asks_num[1] = 0.02*currency_y_b_info_list[3]
    y_b_asks_price[2] = currency_y_b_info_list[4]
    y_b_asks_num[2] = 0.03*currency_y_b_info_list[5]
    y_b_asks_price[3] = currency_y_b_info_list[6]
    y_b_asks_num[3] = 0.04*currency_y_b_info_list[7]
    y_b_asks_price[4] = currency_y_b_info_list[8]
    y_b_asks_num[4] = 0.05*currency_y_b_info_list[9]

    if (y_b_asks_price[1] - y_b_asks_price[0]) / y_b_asks_price[0] > 0.015 or (y_b_asks_price[2] - y_b_asks_price[1]) / y_b_asks_price[1] > 0.015 or (y_b_asks_price[3] - y_b_asks_price[2]) / y_b_asks_price[2] > 0.015 or (y_b_asks_price[4] - y_b_asks_price[3]) / y_b_asks_price[3] > 0.015 :
        return 0

    y_b_bids_price = [0] * 5
    y_b_bids_num = [0] * 5
    y_b_bids_price[0] = currency_y_b_info_list[10]
    y_b_bids_num[0] = 0.01*currency_y_b_info_list[11]
    y_b_bids_price[1] = currency_y_b_info_list[12]
    y_b_bids_num[1] = 0.02*currency_y_b_info_list[13]
    y_b_bids_price[2] = currency_y_b_info_list[14]
    y_b_bids_num[2] = 0.03*currency_y_b_info_list[15]
    y_b_bids_price[3] = currency_y_b_info_list[16]
    y_b_bids_num[3] = 0.04*currency_y_b_info_list[17]
    y_b_bids_price[4] = currency_y_b_info_list[18]
    y_b_bids_num[4] = 0.05*currency_y_b_info_list[19]

    x_b_asks_price = [0] * 5
    x_b_asks_num = [0] * 5
    x_b_asks_price[0] = currency_x_b_info_list[0]
    x_b_asks_num[0] = 0.01*currency_x_b_info_list[1]
    x_b_asks_price[1] = currency_x_b_info_list[2]
    x_b_asks_num[1] = 0.02*currency_x_b_info_list[3]
    x_b_asks_price[2] = currency_x_b_info_list[4]
    x_b_asks_num[2] = 0.03*currency_x_b_info_list[5]
    x_b_asks_price[3] = currency_x_b_info_list[6]
    x_b_asks_num[3] = 0.04*currency_x_b_info_list[7]
    x_b_asks_price[4] = currency_x_b_info_list[8]
    x_b_asks_num[4] = 0.05*currency_x_b_info_list[9]
    #  u'hsr-eth',
    # 1 u'bids': [[0.01105, 2.2376], [0.010981, 16.95], [0.010979, 34], [0.010978, 82.2761], [0.010972, 0.0007], [0.010936, 182.473], [0.010922, 86.7123]],
    # 4 u'asks': [[0.011123, 34], [0.011124, 182.473], [0.01116, 34], [0.011168, 70.8], [0.011173, 56.52], [0.011253, 68], [0.011254, 88.9182]]}

    #   "hsr-btc",
    #  3 "bids": [[0.000872, 25.2303], [0.000871, 384], [0.00087, 241.1533], [0.000869, 20.02], [0.000866, 77.6095]],
    #  2 "asks": [[0.000876, 88.1], [0.000877, 2], [0.000879, 25], [0.00088, 10.78], [0.000881, 2]]}
    # path_info_list
    #   买(eth->hrs)   卖(hrs->btc)   买(btc->mtn)   卖(mtn->eth)
    # [[0,1],[0,1],[0,1,2],[0,1,2,3]]
    # 确定x起
    # x数量 a换程x后累加


    for path in path_list:
        x_part_0_x_cout = 0
        # a数量 累加a数量即可
        x_part_0_a_cout = 0
        x_part_1_a_count = 0
        x_part_1_y_count = 0
        x_part_2_y_count = 0
        x_part_2_b_count = 0
        x_part_3_b_count = 0
        x_end = 0
        i = 0

        # 纪录四个部分的a
        a4_num_record = 0
        a4_price_record = 0

        a3_num_record = 0
        a3_price_record = 0

        a2_num_record = 0
        a2_price_record = 0

        a1_num_record = 0
        a1_price_record = 0
        for part in path:
            if i == 0:
                for ai in part:
                    # price * num
                    # 买(eth->hrs) bid
                    # hrs count
                    # "bids":[[0.01105,2.2376],[0.010981,16.95],[0.010979,34],[0.010978,82.2761],[0.010972,0.0007]]
                    x_part_0_a_cout = x_part_0_a_cout + x_a_asks_num[ai]
                    # x count                               price
                    x_part_0_x_cout = x_part_0_x_cout + x_b_asks_price[ai] * x_a_asks_num[ai]
                    1
                i = i + 1
            elif i == 1:
                for ai in part:
                    # price * num
                    # 卖(hrs->btc) ask
                    # btc count
                    # 上一步算出了 a 货币的数量
                    # "asks":[[0.000876,88.1],[0.000877,2],[0.000879,10],[0.00088,1],[0.000881,1]]
                    # x_part_0_x_cout 0.0052598095
                    # x_part_0_a_cout 19.1876
                    x_part_1_a_count = x_part_1_a_count + y_a_bids_num[ai]
                    # if x_part_0_a_cout > x_part_1_a_count:
                    #     continue
                    # else:
                    #     x_part_1_a_count = x_part_0_a_cout
                    #     break
                # 计算出x_part_1_a_count的实际值 再计算x_part_1_y_count
                if x_part_1_a_count >= x_part_0_a_cout:
                    x_part_1_a_count = x_part_0_a_cout
                x_part_1_a_count_for_calc_y = x_part_1_a_count
                if x_part_1_a_count == x_part_0_a_cout:
                    for ai in part:
                        if x_part_1_a_count_for_calc_y - y_a_bids_num[ai] > 0:
                            x_part_1_y_count = x_part_1_y_count + y_a_bids_num[ai] * y_a_bids_price[ai]
                            x_part_1_a_count_for_calc_y = x_part_1_a_count_for_calc_y - y_a_bids_num[ai]
                        else:
                            x_part_1_y_count = x_part_1_y_count + x_part_1_a_count_for_calc_y * y_a_bids_price[ai]
                            break
                else:
                    for ai in part:
                        x_part_1_y_count = x_part_1_y_count + y_a_bids_num[ai] * y_a_bids_price[ai]
                # 如果 part2 a数量小于 part1的a数量 重新计算x起
                # if x_part_0_a_cout > x_part_1_a_count:
                i = i + 1
            elif i == 2:
                x_part_2_y_count_ax = 0
                for ai in part:
                    # price * num
                    # 买(btc->mtn) bids
                    # mtn count
                    # "bids": [[2.159e-5, 924.04], [2.153e-5, 1330], [2.15e-5, 5000], [2.148e-5, 187.24], [2.141e-5, 8719]]
                    # x_part_1_y_count part2的 y count
                    x_part_2_y_count_ax = x_part_2_y_count_ax + y_b_asks_num[ai] * y_b_asks_price[ai]
                if x_part_1_y_count > x_part_2_y_count_ax:
                    # 如果part3的y数量 小于 part2计算处的y数量 那么part3的y数量等于part3的数量和
                    x_part_2_y_count = x_part_2_y_count_ax
                else:
                    x_part_2_y_count = x_part_1_y_count
                # 算出part3的y 再计算part3的b多少
                x_part_1_y_count_for_calc = x_part_1_y_count
                if (x_part_2_y_count == x_part_1_y_count):
                    # 如果part3的y 等于part2y 说明 已part2y 为主 计算b可取的num
                    for ai in part:
                        if x_part_1_y_count_for_calc - y_b_asks_num[ai] * y_b_asks_price[ai] > 0:
                            x_part_2_b_count = x_part_2_b_count + y_b_asks_num[ai]
                            x_part_1_y_count_for_calc = x_part_1_y_count_for_calc - y_b_asks_num[ai] * \
                                                                                    y_b_asks_price[ai]
                        else:
                            x_part_2_b_count = x_part_2_b_count + x_part_1_y_count_for_calc / y_b_asks_price[ai]
                            break
                else:
                    # 如果part3的y 小于part2y 说明 已part3为主 b的num直接累加即可
                    for ai in part:
                        x_part_2_b_count = x_part_2_b_count + y_b_asks_num[ai]
                i = i + 1
            elif i == 3:
                for ai in part:
                    # price * num
                    # 卖(mtn->eth) asks
                    # eth count
                    # "asks":[[0.00027608,1242.27],[0.00027699,315.48],[0.0002775,461.02],[0.00027965,1350],[0.00028,100.29187725631769]]
                    # part 3 的b 已经算处 要把b卖出去 所以要看下part4中 有多少买b的 换成x
                    # x_part_2_b_count part 3 的b
                    # x_part_3_b_count
                    # x_part_3_x_count
                    x_part_3_b_count = x_part_3_b_count + x_b_bids_num[ai]

                if (x_part_2_b_count < x_part_3_b_count):
                    x_part_3_b_count = x_part_2_b_count
                # 算 x_end
                x_part_3_b_count_for_calc = x_part_3_b_count
                count_record = 0
                for ai in part:
                    if x_part_3_b_count_for_calc - x_b_bids_num[ai] > 0:
                        x_end = x_end + x_b_bids_num[ai] * x_b_bids_price[ai]
                        x_part_3_b_count_for_calc = x_part_3_b_count_for_calc - x_b_bids_num[ai]

                        a4_num_record = a4_num_record + x_b_bids_num[ai]
                        a4_price_record = x_b_bids_price[ai]
                    else:
                        x_end = x_end + x_part_3_b_count_for_calc * x_b_bids_price[ai]
                        # amount  和 price 分别是什么数量和价格—hsr数量 hsreth最低买价
                        a4_num_record = a4_num_record + x_part_3_b_count_for_calc
                        a4_price_record = x_b_bids_price[ai]
                        break
                i = i + 1

        # x_part_3_b_count 算出后 反算x起
        x_part_0_x_cout = 0
        # a数量 累加a数量即可
        x_part_0_a_count_begin = 0
        x_part_1_a_count_begin = 0
        x_part_1_y_count_begin = 0
        x_part_2_y_count_begin = 0
        x_part_2_b_count_begin = 0

        # 买(btc->mtn) bids
        # [[0,1], [0,1,2], [0,1], [0,1,2,3]]
        # "bids": [[2.159e-5, 924.04], [2.153e-5, 1330], [2.15e-5, 5000], [2.148e-5, 187.24], [2.141e-5, 8719]]
        # y_b_bids_price
        # b的数量除以0.998

        a4_num_record = a4_num_record/0.998

        x_part_2_b_count_for_calc = a4_num_record
        count_record = 0
        for ai in path[2]:
            if x_part_2_b_count_for_calc - y_b_asks_num[ai] > 0:

                x_part_2_y_count_begin = x_part_2_y_count_begin + y_b_asks_num[ai] * y_b_asks_price[ai]
                x_part_2_b_count_for_calc = x_part_2_b_count_for_calc - y_b_asks_num[ai]

                a3_num_record = a3_num_record + y_b_asks_num[ai]
                a3_price_record = y_b_asks_price[ai]
            else:
                x_part_2_y_count_begin = x_part_2_y_count_begin + x_part_2_b_count_for_calc * y_b_asks_price[ai]

                # amount  和 price 分别是什么数量和价格—-btc数量 hsrbtc的最高卖价
                a3_price_record = y_b_asks_price[ai]
                a3_num_record = a3_num_record + x_part_2_b_count_for_calc
                x_part_2_b_count_for_calc = 0
                break

        if x_part_2_b_count_for_calc != 0:
            x_part_2_y_count_begin = x_part_2_y_count_begin + x_part_2_b_count_for_calc * a3_price_record

        x_part_2_y_count_begin = x_part_2_y_count_begin/0.998
        # x_part_2_y_count求出来了 求 x_part_1_a_count
        # 卖(hrs->btc) ask
        # btc count
        # 上一步算出了 a 货币的数量
        # "asks":[[0.000876,8.1],[0.000877,2],[0.000879,10],[0.00088,1],[0.000881,1]]
        # "asks": [[0.000876, 88.1], [0.000877, 2], [0.000879, 25], [0.00088, 10.78], [0.000881, 2]]
        # y_a_asks_price
        # amount  和 price 分别是什么数量和价格—swftc数量 swftcbtc最低买价

        x_part_1_y_count_for_calc = x_part_2_y_count_begin
        for ai in path[1]:
            if x_part_1_y_count_for_calc - y_a_bids_price[ai] * y_a_bids_num[ai] > 0:
                x_part_1_a_count_begin = x_part_1_a_count_begin + y_a_bids_num[ai]
                x_part_1_y_count_for_calc = x_part_1_y_count_for_calc - y_a_bids_price[ai] * y_a_bids_num[ai]
                a2_num_record = a2_num_record + x_part_1_y_count_for_calc / y_a_bids_price[ai]
                a2_price_record = y_a_bids_price[ai]
            else:
                x_part_1_a_count_begin = x_part_1_a_count_begin + x_part_1_y_count_for_calc / y_a_bids_price[ai]

                a2_num_record = a2_num_record + x_part_1_y_count_for_calc / y_a_bids_price[ai]
                a2_price_record = y_a_bids_price[ai]
                x_part_1_y_count_for_calc = 0
                break;

        if x_part_1_y_count_for_calc != 0 :
            x_part_1_a_count_begin = x_part_1_a_count_begin + x_part_1_y_count_for_calc/a2_price_record

        x_part_1_a_count_begin = x_part_1_a_count_begin/0.998
        # 最后一步算x起
        # part1 的 a 已经反推出来 最后反推x起
        # x_part_1_a_count_begin
        # price * num
        # 买(eth->hrs) bid
        # hrs count
        # "bids":[[0.01105,2.2376],[0.010981,16.95],[0.010979,34],[0.010978,82.2761],[0.010972,0.0007]]

        x_begin = 0
        x_part_0_a_count_for_calc = x_part_1_a_count_begin
        for ai in path[0]:
            if x_part_0_a_count_for_calc - x_a_asks_num[ai] > 0:

                x_part_0_a_count_begin = x_part_0_a_count_begin + x_a_asks_num[ai]
                x_part_0_a_count_for_calc = x_part_0_a_count_for_calc - x_a_asks_num[ai]


                a1_price_record = x_a_asks_price[ai]

                x_begin = x_begin + x_a_asks_num[ai] * x_a_asks_price[ai]
                a1_num_record = a1_num_record + x_a_asks_num[ai]

            else:
                x_part_0_a_count_begin = x_part_0_a_count_begin + x_part_0_a_count_for_calc

                a1_price_record = x_a_asks_price[ai]

                x_begin = x_begin + x_part_0_a_count_for_calc * x_a_asks_price[ai]
                a1_num_record = a1_num_record + x_part_0_a_count_for_calc
                break

        x_begin=x_begin/0.998

        # a_num_list = [a1_num_record, a2_num_record, a3_num_record, a4_num_record]
        x_a_amount = r.get(currency_a + '-' + 'eth' + '-amount')
        x_a_amount = x_a_amount.decode()

        y_a_amount = r.get(currency_a + '-' + 'btc' + '-amount')
        y_a_amount = y_a_amount.decode()

        y_b_amount = r.get(currency_b + '-' + 'btc' + '-amount')
        y_b_amount = y_b_amount.decode()

        x_b_amount = r.get(currency_b + '-' + 'eth' + '-amount')
        x_b_amount = x_b_amount.decode()

        x_a_price = r.get(currency_a + '-' + 'eth' + '-price')
        x_a_price = x_a_price.decode()

        y_a_price = r.get(currency_a + '-' + 'btc' + '-price')
        y_a_price = y_a_price.decode()

        y_b_price = r.get(currency_b + '-' + 'btc' + '-price')
        y_b_price = y_b_price.decode()

        x_b_price = r.get(currency_b + '-' + 'eth' + '-price')
        x_b_price = x_b_price.decode()


        log_info_list.append('未求精度的数量'+str(a1_num_record)+' '+str(a2_num_record)+' '+str(a3_num_record)+' '+str(a4_num_record))

        amount_1 = '%.' + x_a_amount + 'f'
        amount_2 = '%.' + y_a_amount + 'f'
        amount_3 = '%.' + y_b_amount + 'f'
        amount_4 = '%.' + x_b_amount + 'f'

        price_1 = '%.' + x_a_price + 'f'
        price_2 = '%.' + y_a_price + 'f'
        price_3 = '%.' + y_b_price + 'f'
        price_4 = '%.' + x_b_price + 'f'

        a1_done = (amount_1 % float(a1_num_record))


        a2_num_record = float(a1_done)*0.998
        a2_done = (amount_2 % float(a2_num_record))


        a4_done = (amount_4 % float(a4_num_record))

        a3_num_record = float(a4_done)*0.998
        a3_done = (amount_3 % float(a3_num_record))

        p1_done = (price_1 % float(a1_price_record))
        p2_done = (price_2 % float(a2_price_record))
        p3_done = (price_3 % float(a3_price_record))
        p4_done = (price_4 % float(a4_price_record))

        a_num_list = [a1_done, a2_done, a4_done, a3_done]
        a_price_list = [p1_done, p2_done, p3_done, p4_done]

        # print('------------------------------------------------------')
        # print('pid: ' + pid + '--', x_begin * 1.05, x_end * 0.998 * 0.998 * 0.998 * 0.998,
        #        x_begin * 1.005 < x_end * 0.998 * 0.998 * 0.998 * 0.998, a_num_list, a_price_list)
        #print(path)
        log_info_list.append('pid: ' + str(pid) + '--'+ str(x_begin * 1.05)+str(x_end)+
                             str(x_begin * 1.005 < x_end )+
                             a1_done+','+a2_done+','+a3_done+','+a4_done+','
                             +p1_done+','+p2_done+','+p3_done+','+p4_done
                             )

        log_switch = r.get('log_switch')
        if log_switch != None:
            if(log_switch.decode() == currency_b):
                for log in log_info_list:
                    logger.info(log)

        if x_end  / x_begin < 1.005:
            break

        if   float(a2_done) * float(a4_done) == float('0'):
            for log in log_info_list:
                logger.info(log)
            continue

        if x_end  / x_begin <= last_ratio:
            log_info_list.append('此次比例:' + str(x_end/x_begin) +' 低于或等于上次计算比例:' + str(last_ratio))
            return last_ratio
        # if x_begin < x_end * 0.998 * 0.998 * 0.998 * 0.998 and x_end * 0.998 * 0.998 * 0.998 * 0.998 / x_begin > 1.005:
        #     # if x_begin < x_end * 0.998 * 0.998 * 0.998 * 0.998:
        # print('pid: ' + pid + '--', x_begin , x_end * 0.998 * 0.998 * 0.998 * 0.998,
        #       x_begin * 1.005 < x_end * 0.998 * 0.998 * 0.998 * 0.998, a_num_list, a_price_list)
        # print(path)
        log_info_list.append('此次比例:' + str(x_end / x_begin) + ' 高于上次计算比例:' + str(last_ratio))
        last_ratio = x_end / x_begin

        for log in log_info_list:
            logger.info(log)
        #放redis-list
        result_list_redis(r, currency_a, currency_b, a_num_list, a_price_list,platform,x_begin,x_part_2_y_count_begin,x_end)

    return last_ratio

def result_list_redis(r,currency_a,currency_b,a_num_list,a_price_record,platform,x_begin,y_middle,x_end):
    # {"path": [{"from": "iost", "to": "eth", "type": "buy", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "iost", "to": "btc", "type": "sell", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "ht", "to": "btc", "type": "buy", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "ht", "to": "eth", "type": "sell", "market": "false", "amount": "1", "price": "1"}],
    #  "platform": "huobi", "action": "PutFourPointArbitrage"}

    result_dict={}
    result_path_dict_list=[]

    #{"from": "iost", "to": "eth", "type": "buy", "market": "false", "amount": "1", "price": "1"}

    path1 = {'from': currency_a, 'to': 'eth', 'type': 'buy', 'market': 'false', 'amount': a_num_list[0],'price': a_price_record[0],'xbegin':x_begin}

    path2 = {'from': currency_a, 'to': 'btc', 'type': 'sell', 'market': 'false', 'amount': a_num_list[1],'price': a_price_record[1]}

    path3 = {'from': currency_b, 'to': 'btc', 'type': 'buy', 'market': 'false', 'amount': a_num_list[2],'price': a_price_record[2],'ymiddle':y_middle}

    path4 = {'from': currency_b, 'to': 'eth', 'type': 'sell', 'market': 'false', 'amount': a_num_list[3],'price': a_price_record[3],'xend':x_end}

    result_path_dict_list = [path1, path2, path3, path4]
    result_dict['platform']=platform
    result_dict['action']='PutFourPointArbitrage'
    result_dict['path']=result_path_dict_list
    result_json =  json.dumps(result_dict)
    # print("赚钱路径")
    # print('pid: ' +str(os.getpid())+'-'+currency_a+'-'+currency_b+'--'+result_json)
    r.lpush("list_result",result_json)


def recalc_profit(r, currency_a,currency_b,step,logger,recalc_info_json,platform):

    #currency_name = mtn
    #os.pid
    pid =str(os.getpid())
    if currency_a == currency_b:
        return 'false'
    #检查货币信息
    log_info_list=[]
    #print('pid: ' +pid+ '++'+currency_a+'----------'+currency_b)
    log_info_list.append('pid: ' +pid+ ' : '+currency_a+'-------------------------------------------'+currency_b)
    if r.get(currency_b  + '-'+ 'btc') == '':
        return 'false'
    if r.get(currency_b + '-' + 'eth') == '':
        return 'false'

    key_pre = currency_a + '-' + 'eth'
    test_null = r.get(key_pre + '_ask_price_0')
    if(test_null == None):
        return 'false'
    currency_x_a_list =[
        key_pre + '_ask_price_0', key_pre + '_ask_num_0', #0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1', #2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2', #4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3', #6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4', #8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0', #10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1', #12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2', #14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3', #16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  #18 19
    ]

    currency_x_a_info_list = r.mget(currency_x_a_list)
    currency_x_a_info_list=string_to_float_list(currency_x_a_info_list)

    str_print=""
    ii = 1;
    for elem in currency_x_a_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii+1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_a + '-eth-'+str_print)
    #print('pid: ' + pid + '--' + currency_a + '-eth-'+str_print)

    str_print = ""

    # mtn的价格 x b
    key_pre = currency_b + '-' + 'eth'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 'false'
    currency_x_b_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_x_b_info_list = r.mget(currency_x_b_list)
    currency_x_b_info_list = string_to_float_list(currency_x_b_info_list)

    str_print = ""
    for elem in currency_x_b_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_b + '-eth-' + str_print)
    #print('pid: ' + pid + '--' + currency_b + '-eth-' + str_print)

    str_print = ""
    # 前20是mtn价格和数量 后20是hrs价格和数量

    #btc对应信息
    #hrs y a
    key_pre = currency_a + '-' + 'btc'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 'false'
    currency_y_a_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_y_a_info_list = r.mget(currency_y_a_list)
    currency_y_a_info_list = string_to_float_list(currency_y_a_info_list)

    str_print = ""
    for elem in currency_y_a_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_a + '-btc-' + str_print)
    #print('pid: ' + pid + '--' + currency_a + '-btc-' + str_print)

    str_print = ""

    # mtn的价格 y b
    key_pre = currency_b + '-' + 'btc'
    test_null = r.get(key_pre + '_ask_price_0')
    if (test_null == None):
        return 'false'
    currency_y_b_list = [
        key_pre + '_ask_price_0', key_pre + '_ask_num_0',  # 0 1
        key_pre + '_ask_price_1', key_pre + '_ask_num_1',  # 2 3
        key_pre + '_ask_price_2', key_pre + '_ask_num_2',  # 4 5
        key_pre + '_ask_price_3', key_pre + '_ask_num_3',  # 6 7
        key_pre + '_ask_price_4', key_pre + '_ask_num_4',  # 8 9
        key_pre + '_bid_price_0', key_pre + '_bid_num_0',  # 10 11
        key_pre + '_bid_price_1', key_pre + '_bid_num_1',  # 12 13
        key_pre + '_bid_price_2', key_pre + '_bid_num_2',  # 14 15
        key_pre + '_bid_price_3', key_pre + '_bid_num_3',  # 16 17
        key_pre + '_bid_price_4', key_pre + '_bid_num_4'  # 18 19
    ]
    currency_y_b_info_list = r.mget(currency_y_b_list)
    currency_y_b_info_list = string_to_float_list(currency_y_b_info_list)


    for elem in currency_y_b_info_list:
        str_print = str_print + '^' + str(elem)
        if ii == 10:
            str_print = str_print + "*********"
        ii = ii + 1
    ii = 1;
    log_info_list.append('pid: ' + pid + '--' + currency_b + '-btc-' + str_print)
    #print('pid: ' + pid + '--' + currency_b + '-btc-' + str_print)

    x_a_bids_price = [0] * 5
    x_a_bids_num = [0] * 5
    x_a_bids_price[0] = currency_x_a_info_list[10] #price
    x_a_bids_num[0] = 0.01*currency_x_a_info_list[11]   #num
    x_a_bids_price[1] = currency_x_a_info_list[12]
    x_a_bids_num[1] = 0.02*currency_x_a_info_list[13]
    x_a_bids_price[2] = currency_x_a_info_list[14]
    x_a_bids_num[2] = 0.03*currency_x_a_info_list[15]
    x_a_bids_price[3] = currency_x_a_info_list[16]
    x_a_bids_num[3] = 0.04*currency_x_a_info_list[17]
    x_a_bids_price[4] = currency_x_a_info_list[18]
    x_a_bids_num[4] = 0.05*currency_x_a_info_list[19]

    y_a_asks_price = [0] * 5
    y_a_asks_num = [0] * 5
    y_a_asks_price[0] = currency_y_a_info_list[0] #price
    y_a_asks_num[0] = 0.01*currency_y_a_info_list[1]   #num
    y_a_asks_price[1] = currency_y_a_info_list[2]
    y_a_asks_num[1] = 0.02*currency_y_a_info_list[3]
    y_a_asks_price[2] = currency_y_a_info_list[4]
    y_a_asks_num[2] = 0.03*currency_y_a_info_list[5]
    y_a_asks_price[3] = currency_y_a_info_list[6]
    y_a_asks_num[3] = 0.04*currency_y_a_info_list[7]
    y_a_asks_price[4] = currency_y_a_info_list[8]
    y_a_asks_num[4] = 0.05*currency_y_a_info_list[9]

    y_a_bids_price = [0] * 5
    y_a_bids_num = [0] * 5
    y_a_bids_price[0] = currency_y_a_info_list[10] #price
    y_a_bids_num[0] = 0.01*currency_y_a_info_list[11]   #num
    y_a_bids_price[1] = currency_y_a_info_list[12]
    y_a_bids_num[1] = 0.02*currency_y_a_info_list[13]
    y_a_bids_price[2] = currency_y_a_info_list[14]
    y_a_bids_num[2] = 0.03*currency_y_a_info_list[15]
    y_a_bids_price[3] = currency_y_a_info_list[16]
    y_a_bids_num[3] = 0.04*currency_y_a_info_list[17]
    y_a_bids_price[4] = currency_y_a_info_list[18]
    y_a_bids_num[4] = 0.05*currency_y_a_info_list[19]

    x_a_asks_price = [0] * 5
    x_a_asks_num = [0] * 5
    x_a_asks_price[0] = currency_x_a_info_list[0]
    x_a_asks_num[0] = 0.01*currency_x_a_info_list[1]
    x_a_asks_price[1] = currency_x_a_info_list[2]
    x_a_asks_num[1] = 0.02*currency_x_a_info_list[3]
    x_a_asks_price[2] = currency_x_a_info_list[4]
    x_a_asks_num[2] = 0.03*currency_x_a_info_list[5]
    x_a_asks_price[3] = currency_x_a_info_list[6]
    x_a_asks_num[3] = 0.04*currency_x_a_info_list[7]
    x_a_asks_price[4] = currency_x_a_info_list[8]
    x_a_asks_num[4] = 0.05*currency_x_a_info_list[9]

    x_b_bids_price = [0] * 5
    x_b_bids_num = [0] * 5
    x_b_bids_price[0] = currency_x_b_info_list[10]
    x_b_bids_num[0] = 0.01*currency_x_b_info_list[11]
    x_b_bids_price[1] = currency_x_b_info_list[12]
    x_b_bids_num[1] = 0.02*currency_x_b_info_list[13]
    x_b_bids_price[2] = currency_x_b_info_list[14]
    x_b_bids_num[2] = 0.03*currency_x_b_info_list[15]
    x_b_bids_price[3] = currency_x_b_info_list[16]
    x_b_bids_num[3] = 0.04*currency_x_b_info_list[17]
    x_b_bids_price[4] = currency_x_b_info_list[18]
    x_b_bids_num[4] = 0.05*currency_x_b_info_list[19]

    y_b_asks_price = [0] * 5
    y_b_asks_num = [0] * 5
    y_b_asks_price[0] = currency_y_b_info_list[0]
    y_b_asks_num[0] = 0.01*currency_y_b_info_list[1]
    y_b_asks_price[1] = currency_y_b_info_list[2]
    y_b_asks_num[1] = 0.02*currency_y_b_info_list[3]
    y_b_asks_price[2] = currency_y_b_info_list[4]
    y_b_asks_num[2] = 0.03*currency_y_b_info_list[5]
    y_b_asks_price[3] = currency_y_b_info_list[6]
    y_b_asks_num[3] = 0.04*currency_y_b_info_list[7]
    y_b_asks_price[4] = currency_y_b_info_list[8]
    y_b_asks_num[4] = 0.05*currency_y_b_info_list[9]

    y_b_bids_price = [0] * 5
    y_b_bids_num = [0] * 5
    y_b_bids_price[0] = currency_y_b_info_list[10]
    y_b_bids_num[0] = 0.01*currency_y_b_info_list[11]
    y_b_bids_price[1] = currency_y_b_info_list[12]
    y_b_bids_num[1] = 0.02*currency_y_b_info_list[13]
    y_b_bids_price[2] = currency_y_b_info_list[14]
    y_b_bids_num[2] = 0.03*currency_y_b_info_list[15]
    y_b_bids_price[3] = currency_y_b_info_list[16]
    y_b_bids_num[3] = 0.04*currency_y_b_info_list[17]
    y_b_bids_price[4] = currency_y_b_info_list[18]
    y_b_bids_num[4] = 0.05*currency_y_b_info_list[19]

    x_b_asks_price = [0] * 5
    x_b_asks_num = [0] * 5
    x_b_asks_price[0] = currency_x_b_info_list[0]
    x_b_asks_num[0] = 0.01*currency_x_b_info_list[1]
    x_b_asks_price[1] = currency_x_b_info_list[2]
    x_b_asks_num[1] = 0.02*currency_x_b_info_list[3]
    x_b_asks_price[2] = currency_x_b_info_list[4]
    x_b_asks_num[2] = 0.03*currency_x_b_info_list[5]
    x_b_asks_price[3] = currency_x_b_info_list[6]
    x_b_asks_num[3] = 0.04*currency_x_b_info_list[7]
    x_b_asks_price[4] = currency_x_b_info_list[8]
    x_b_asks_num[4] = 0.05*currency_x_b_info_list[9]

    a2_num_record = 0
    a2_price_record = 0

    a3_num_record = 0
    a3_price_record = 0

    a4_num_record = 0
    a4_price_record = 0

    x_begin = 0
    x_end = 0

    y_3_begin_for_calc=0

    uniqid =''
    status = ()

    if int(step) == 2:
        x_begin = recalc_info_json['path'][0]['xbegin']
        a_begin = recalc_info_json['path'][0]['amount']
        a1_num_record = recalc_info_json['path'][0]['amount']
        a1_price_record = recalc_info_json['path'][0]['price']
        uniqid=recalc_info_json['uniqid']
        status = (2,0,0,0)

    elif int(step) == 3:
        x_begin = recalc_info_json['path'][0]['xbegin']
        y_middle = recalc_info_json['path'][2]['ymiddle']
        a1_num_record = recalc_info_json['path'][0]['amount']
        a1_price_record = recalc_info_json['path'][0]['price']
        a2_num_record = recalc_info_json['path'][1]['amount']
        a2_price_record = recalc_info_json['path'][1]['price']
        uniqid = recalc_info_json['uniqid']
        status = (2, 2, 0, 0)

    #正推计算
    # 计算part2的y起
    if step == 2 :
        a_2_begin_for_calc = float(a_begin) * 0.998
        a2_num_record = a_2_begin_for_calc
        y_2_sum = 0
        for ai in range(4):
            if a_2_begin_for_calc - y_a_bids_num[ai] > 0:
                y_2_sum = y_2_sum = y_a_bids_price[ai] * y_a_bids_num[ai]
                a_2_begin_for_calc = a_2_begin_for_calc - y_a_bids_num[ai]
                a2_price_record = y_a_bids_price[ai]
            else:
                y_2_sum = a_2_begin_for_calc * y_a_bids_price[ai]
                a_2_begin_for_calc = 0
                a2_price_record = x_a_bids_price[ai]
                break

        if a_2_begin_for_calc != 0:
            return 'false'


        y_3_begin = y_2_sum * 0.998
        y_middle = y_3_begin
        y_3_begin_for_calc = y_3_begin

    b_3_sum = 0
    if step == 3:
        # 计算part3的b_begin

        y_3_begin_for_calc = float(y_middle) * 0.998

    for ai in range(4):
        if y_3_begin_for_calc - y_b_asks_num[ai] * y_b_asks_price[ai] > 0:
            b_3_sum = b_3_sum + y_b_asks_num[ai]
            y_3_begin_for_calc = y_3_begin_for_calc - y_b_asks_num[ai] * y_b_asks_price[ai]
            a3_price_record = y_b_asks_price[ai]
        else:
            b_3_sum = b_3_sum + y_3_begin_for_calc / y_b_asks_price[ai]
            y_3_begin_for_calc = 0
            a3_price_record = y_b_asks_price[ai]
            break

    if y_3_begin_for_calc != 0:
        return 'false'

    a3_num_record = b_3_sum
    b_4_begin = b_3_sum * 0.998
    b_4_begin_for_calc = b_4_begin
    a_4_sum = 0

    a4_num_record = b_4_begin
    for ai in range(4):
        if b_4_begin_for_calc - x_b_bids_num[ai] > 0:
            a_4_sum = a_4_sum + x_b_bids_num[ai]
            b_4_begin_for_calc = b_4_begin_for_calc - x_b_bids_num[ai]
            x_end = x_end + x_b_bids_num[ai] * x_b_bids_price[ai]
            a4_price_record = x_b_bids_price[ai]
        else:
            a_4_sum = a_4_sum + b_4_begin_for_calc
            x_end = x_end + b_4_begin_for_calc * x_b_bids_price[ai]
            b_4_begin_for_calc = 0
            a4_price_record = x_b_bids_price[ai]
            break

    x_a_amount = r.get(currency_a + '-' + 'eth' + '-amount')
    x_a_amount = x_a_amount.decode()

    y_a_amount = r.get(currency_a + '-' + 'btc' + '-amount')
    y_a_amount = y_a_amount.decode()

    y_b_amount = r.get(currency_b + '-' + 'btc' + '-amount')
    y_b_amount = y_b_amount.decode()

    x_b_amount = r.get(currency_b + '-' + 'eth' + '-amount')
    x_b_amount = x_b_amount.decode()

    x_a_price = r.get(currency_a + '-' + 'eth' + '-price')
    x_a_price = x_a_price.decode()

    y_a_price = r.get(currency_a + '-' + 'btc' + '-price')
    y_a_price = y_a_price.decode()

    y_b_price = r.get(currency_b + '-' + 'btc' + '-price')
    y_b_price = y_b_price.decode()

    x_b_price = r.get(currency_b + '-' + 'eth' + '-price')
    x_b_price = x_b_price.decode()

    log_info_list.append(
        '未求精度的数量' + str(a1_num_record) + ' ' + str(a2_num_record) + ' ' + str(a3_num_record) + ' ' + str(a4_num_record))

    amount_1 = '%.' + x_a_amount + 'f'
    amount_2 = '%.' + y_a_amount + 'f'
    amount_3 = '%.' + y_b_amount + 'f'
    amount_4 = '%.' + x_b_amount + 'f'

    price_1 = '%.' + x_a_price + 'f'
    price_2 = '%.' + y_a_price + 'f'
    price_3 = '%.' + y_b_price + 'f'
    price_4 = '%.' + x_b_price + 'f'

    a1_done = (amount_1 % float(a1_num_record))
    a2_done = (amount_2 % float(a2_num_record))
    a3_done = (amount_3 % float(a3_num_record))
    a4_done = (amount_4 % float(a4_num_record))

    p1_done = (price_1 % float(a1_price_record))
    p2_done = (price_2 % float(a2_price_record))
    p3_done = (price_3 % float(a3_price_record))
    p4_done = (price_4 % float(a4_price_record))

    a_num_list = [a1_done, a2_done, a3_done, a4_done]
    a_price_list = [p1_done, p2_done, p3_done, p4_done]

    # print('------------------------------------------------------')
    # print('pid: ' + pid + '--', x_begin * 1.05, x_end * 0.998 * 0.998 * 0.998 * 0.998,
    #        x_begin * 1.005 < x_end * 0.998 * 0.998 * 0.998 * 0.998, a_num_list, a_price_list)
    # print(path)
    flag = float(x_begin) * 1.005 < x_end
    log_info_list.append('pid: ' + str(pid) + '--' + str(float(x_begin) * 1.05) +'---'+str(x_end) +'---'+
                         str(float(x_begin) * 1.005 < x_end) +
                         a1_done + ',' + a2_done + ',' + a3_done + ',' + a4_done + ','
                         + p1_done + ',' + p2_done + ',' + p3_done + ',' + p4_done
                         )

    log_switch = r.get('log_recalc')
    if log_switch != None:
        if (log_switch.decode() == 'ture'):
            for log in log_info_list:
                logger.info(log)

    if x_end / float(x_begin) < 1.005:
        return 'false'

    if float(a2_done) * float(a4_done) == float('0'):
        for log in log_info_list:
            logger.info(log)
        return 'false'
    # if x_begin < x_end * 0.998 * 0.998 * 0.998 * 0.998 and x_end * 0.998 * 0.998 * 0.998 * 0.998 / x_begin > 1.005:
    #     # if x_begin < x_end * 0.998 * 0.998 * 0.998 * 0.998:
    # print('pid: ' + pid + '--', x_begin , x_end * 0.998 * 0.998 * 0.998 * 0.998,
    #       x_begin * 1.005 < x_end * 0.998 * 0.998 * 0.998 * 0.998, a_num_list, a_price_list)
    # print(path)
    for log in log_info_list:
        logger.info(log)
    # 放redis-list
    result_list_redis_recalc(r, currency_a, currency_b, a_num_list, a_price_list, platform, x_begin, y_middle,x_end,uniqid,status)

    return 'ture'



def recalc(redisip_redisport_platform):
    r = redis.Redis(host=redisip_redisport_platform[0],
                    port=redisip_redisport_platform[1])
    ppid = os.getpid()
    logger = tools.logger.Logger(str(ppid) + 'recalc', str(ppid) + 'recalc.log')
    platform = redisip_redisport_platform[2]
    while True:
        recalc_info_byte = r.lpop("list_recalc")
        if recalc_info_byte == None or recalc_info_byte == '':
            continue
        try:
            recalc_info_str = recalc_info_byte.decode()
            logger.info(str(time.time()))
            logger.info(recalc_info_str)
            recalc_info_json = json.loads(recalc_info_str)
            currency_a = recalc_info_json['path'][0]['from']
            currency_b = recalc_info_json['path'][3]['from']
            step_1_status = recalc_info_json['path'][0]['status']
            step_2_status = recalc_info_json['path'][1]['status']
            step_3_status = recalc_info_json['path'][2]['status']
            step_4_status = recalc_info_json['path'][3]['status']
            step = 0
            if int(step_2_status) == 3:
                step = 2
                x_begin = recalc_info_json['path'][0]['xbegin']
            elif int(step_3_status) == 3:
                step = 3
                x_begin = recalc_info_json['path'][0]['xbegin']
                y_middle = recalc_info_json['path'][2]['ymiddle']
            else:
                continue
            recalc_result = 'false'
            while True:
                recalc_result = recalc_profit(r, currency_a, currency_b, step, logger, recalc_info_json, platform)
                if recalc_result == 'ture':
                    break
            logger.info(str(time.time()))
        except Exception as e:
            logger.info(str(e))
            msg = traceback.format_exc()
            logger.info(msg)
    return

def result_list_redis_recalc(r,currency_a,currency_b,a_num_list,a_price_record,platform,x_begin,y_middle,x_end,uniqid,status):
    # {"path": [{"from": "iost", "to": "eth", "type": "buy", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "iost", "to": "btc", "type": "sell", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "ht", "to": "btc", "type": "buy", "market": "false", "amount": "1", "price": "1"},
    #           {"from": "ht", "to": "eth", "type": "sell", "market": "false", "amount": "1", "price": "1"}],
    #  "platform": "huobi", "action": "PutFourPointArbitrage"}

    result_dict={}
    result_path_dict_list=[]

    #{"from": "iost", "to": "eth", "type": "buy", "market": "false", "amount": "1", "price": "1"}

    path1 = {'from': currency_a, 'to': 'eth', 'type': 'buy', 'market': 'false', 'amount': a_num_list[0],'price': a_price_record[0],'xbegin':x_begin,'status':status[0]}

    path2 = {'from': currency_a, 'to': 'btc', 'type': 'sell', 'market': 'false', 'amount': a_num_list[1],'price': a_price_record[1],'status':status[1]}

    path3 = {'from': currency_b, 'to': 'btc', 'type': 'buy', 'market': 'false', 'amount': a_num_list[2],'price': a_price_record[2],'ymiddle':y_middle,'status':status[2]}

    path4 = {'from': currency_b, 'to': 'eth', 'type': 'sell', 'market': 'false', 'amount': a_num_list[3],'price': a_price_record[3],'xend':x_end,'status':status[3]}

    result_path_dict_list = [path1, path2, path3, path4]
    result_dict['platform']=platform
    result_dict['action']='PutRback'
    result_dict['uniqid'] = uniqid
    result_dict['path']=result_path_dict_list
    result_json =  json.dumps(result_dict)
    # print("赚钱路径")
    # print('pid: ' +str(os.getpid())+'-'+currency_a+'-'+currency_b+'--'+result_json)
    r.lpush("list_result",result_json)

# hsr_eth='{"action":"MarketDepthData","platform":"huobi","symbol":"hsreth","asks":[[0.0007722,12.4201],[0.00077226,14],[0.00077338,82],[0.000774,681.6],[0.000775,117.99]],"bids":[[0.00077052,2.6126],[0.000769,333.9326],[0.00076761,30],[0.00076721,1.3565],[0.000767,415.2]],"timestamp":1523415065}'
# hsr_btc='{"action":"MarketDepthData","platform":"huobi","symbol":"hsrbtc","asks":[[0.0007722,12.4201],[0.00077226,14],[0.00077338,82],[0.000774,681.6],[0.000775,117.99]],"bids":[[0.00077425,36.7906],[0.00076483,19],[0.00076761,30],[0.00076721,1.3565],[0.000767,415.2]],"timestamp":1523415065}'
# path = '/Users/yangxi/projectpython/rectangle-arbitrage/data/paths_result.dat'
# f = open(path, 'r')
# path_list = []
# for line in f.readlines():
#     line = line.strip()
#     a = json.loads(line)
#     path_list.append(a)
# #calc_fork(currency_path_platform_redis_ip_redis_port)
# calc_fork(('mtn',path_list,'huobi','127.0.0.1','6380'))


# recalc(('127.0.0.1','6380','huobi'))