#!/usr/bin/python
# -*- coding:utf8 -*-
import os
from multiprocessing import Pool
import json
import redis
import time


def string_to_float_list(string_list):
    for i in range(20):
        string_list[i] = float(string_list[i])
    return string_list

def calc_fork(currency_b):
    pool = redis.ConnectionPool(host='127.0.0.1', port=6379,
                                decode_responses=True)  # host是redis主机，需要redis服务端和客户端都起着 redis默认端口是6379
    r = redis.Redis(connection_pool=pool)
    print("计算货币:"+currency_b)
    r.set('1111','1111')
    #获取路径
    redis_list_key = 'list_'+currency_b
    path_info=[[0,1],[0,1],[0,1,2],[0,1,2,3]]
    while True:
        currency_info_str = r.lpop(redis_list_key)  # ws.send()验证信息
        if (currency_info_str == None):
            print("数据空fork")
            time.sleep(1);
            continue
        currency_info_dict = json.loads(currency_info_str)
        print("计算:" + currency_info_str)
        print("计算:" + currency_b)
        calc_profit(r,currency_info_dict,currency_info_str,path_info)
        time.sleep(1);


def calc_profit(r, currency_a,currency_b, path_list):
    #currency_name = mtn
    #检查货币信息

    if r.get(currency_b  + '-'+ 'btc') == '':
        return
    if r.get(currency_b + '-' + 'eth') == '':
        return
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

    # mtn的价格 x b
    key_pre = currency_b + '-' + 'eth'
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
    #前20是mtn价格和数量 后20是hrs价格和数量

    #btc对应信息
    #hrs y a
    key_pre = currency_a + '-' + 'btc'
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

    # mtn的价格 y b
    key_pre = currency_b + '-' + 'btc'
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

    x_a_bids_price = [0] * 5
    x_a_bids_num = [0] * 5
    x_a_bids_price[0] = currency_x_a_info_list[10] #price
    x_a_bids_num[0] = currency_x_a_info_list[11]   #num
    x_a_bids_price[1] = currency_x_a_info_list[12]
    x_a_bids_num[1] = currency_x_a_info_list[13]
    x_a_bids_price[2] = currency_x_a_info_list[14]
    x_a_bids_num[2] = currency_x_a_info_list[15]
    x_a_bids_price[3] = currency_x_a_info_list[16]
    x_a_bids_num[3] = currency_x_a_info_list[17]
    x_a_bids_price[4] = currency_x_a_info_list[18]
    x_a_bids_num[4] = currency_x_a_info_list[19]

    y_a_asks_price = [0] * 5
    y_a_asks_num = [0] * 5
    y_a_asks_price[0] = currency_y_a_info_list[0] #price
    y_a_asks_num[0] = currency_y_a_info_list[1]   #num
    y_a_asks_price[1] = currency_y_a_info_list[2]
    y_a_asks_num[1] = currency_y_a_info_list[3]
    y_a_asks_price[2] = currency_y_a_info_list[4]
    y_a_asks_num[2] = currency_y_a_info_list[5]
    y_a_asks_price[3] = currency_y_a_info_list[6]
    y_a_asks_num[3] = currency_y_a_info_list[7]
    y_a_asks_price[4] = currency_y_a_info_list[8]
    y_a_asks_num[4] = currency_y_a_info_list[9]

    y_a_bids_price = [0] * 5
    y_a_bids_num = [0] * 5
    y_a_bids_price[0] = currency_y_a_info_list[10] #price
    y_a_bids_num[0] = currency_y_a_info_list[11]   #num
    y_a_bids_price[1] = currency_y_a_info_list[12]
    y_a_bids_num[1] = currency_y_a_info_list[13]
    y_a_bids_price[2] = currency_y_a_info_list[14]
    y_a_bids_num[2] = currency_y_a_info_list[15]
    y_a_bids_price[3] = currency_y_a_info_list[16]
    y_a_bids_num[3] = currency_y_a_info_list[17]
    y_a_bids_price[4] = currency_y_a_info_list[18]
    y_a_bids_num[4] = currency_y_a_info_list[19]

    x_a_asks_price = [0] * 5
    x_a_asks_num = [0] * 5
    x_a_asks_price[0] = currency_x_a_info_list[0]
    x_a_asks_num[0] = currency_x_a_info_list[1]
    x_a_asks_price[1] = currency_x_a_info_list[2]
    x_a_asks_num[1] = currency_x_a_info_list[3]
    x_a_asks_price[2] = currency_x_a_info_list[4]
    x_a_asks_num[2] = currency_x_a_info_list[5]
    x_a_asks_price[3] = currency_x_a_info_list[6]
    x_a_asks_num[3] = currency_x_a_info_list[7]
    x_a_asks_price[4] = currency_x_a_info_list[8]
    x_a_asks_num[4] = currency_x_a_info_list[9]

    x_b_bids_price = [0] * 5
    x_b_bids_num = [0] * 5
    x_b_bids_price[0] = currency_x_b_info_list[10]
    x_b_bids_num[0] = currency_x_b_info_list[11]
    x_b_bids_price[1] = currency_x_b_info_list[12]
    x_b_bids_num[1] = currency_x_b_info_list[13]
    x_b_bids_price[2] = currency_x_b_info_list[14]
    x_b_bids_num[2] = currency_x_b_info_list[15]
    x_b_bids_price[3] = currency_x_b_info_list[16]
    x_b_bids_num[3] = currency_x_b_info_list[17]
    x_b_bids_price[4] = currency_x_b_info_list[18]
    x_b_bids_num[4] = currency_x_b_info_list[19]

    y_b_asks_price = [0] * 5
    y_b_asks_num = [0] * 5
    y_b_asks_price[0] = currency_y_b_info_list[0]
    y_b_asks_num[0] = currency_y_b_info_list[1]
    y_b_asks_price[1] = currency_y_b_info_list[2]
    y_b_asks_num[1] = currency_y_b_info_list[3]
    y_b_asks_price[2] = currency_y_b_info_list[4]
    y_b_asks_num[2] = currency_y_b_info_list[5]
    y_b_asks_price[3] = currency_y_b_info_list[6]
    y_b_asks_num[3] = currency_y_b_info_list[7]
    y_b_asks_price[4] = currency_y_b_info_list[8]
    y_b_asks_num[4] = currency_y_b_info_list[9]

    y_b_bids_price = [0] * 5
    y_b_bids_num = [0] * 5
    y_b_bids_price[0] = currency_y_b_info_list[10]
    y_b_bids_num[0] = currency_y_b_info_list[11]
    y_b_bids_price[1] = currency_y_b_info_list[12]
    y_b_bids_num[1] = currency_y_b_info_list[13]
    y_b_bids_price[2] = currency_y_b_info_list[14]
    y_b_bids_num[2] = currency_y_b_info_list[15]
    y_b_bids_price[3] = currency_y_b_info_list[16]
    y_b_bids_num[3] = currency_y_b_info_list[17]
    y_b_bids_price[4] = currency_y_b_info_list[18]
    y_b_bids_num[4] = currency_y_b_info_list[19]

    x_b_asks_price = [0] * 5
    x_b_asks_num = [0] * 5
    x_b_asks_price[0] = currency_x_b_info_list[0]
    x_b_asks_num[0] = currency_x_b_info_list[1]
    x_b_asks_price[1] = currency_x_b_info_list[2]
    x_b_asks_num[1] = currency_x_b_info_list[3]
    x_b_asks_price[2] = currency_x_b_info_list[4]
    x_b_asks_num[2] = currency_x_b_info_list[5]
    x_b_asks_price[3] = currency_x_b_info_list[6]
    x_b_asks_num[3] = currency_x_b_info_list[7]
    x_b_asks_price[4] = currency_x_b_info_list[8]
    x_b_asks_num[4] = currency_x_b_info_list[9]
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
    for part in path_list:
        if i == 0:
            for ai in part:
                # price * num
                # 买(eth->hrs) bid
                # hrs count
                # "bids":[[0.01105,2.2376],[0.010981,16.95],[0.010979,34],[0.010978,82.2761],[0.010972,0.0007]]
                x_part_0_a_cout = x_part_0_a_cout + x_a_bids_num[ai]
                # x count                               price
                x_part_0_x_cout = x_part_0_x_cout + x_b_bids_price[ai] * x_a_bids_num[ai]
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
                x_part_1_a_count = x_part_1_a_count + y_a_asks_num[ai]
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
                    if x_part_1_a_count_for_calc_y - y_a_asks_num[ai] > 0:
                        x_part_1_y_count = x_part_1_y_count + y_a_asks_num[ai] * y_a_asks_price[ai]
                        x_part_1_a_count_for_calc_y = x_part_1_a_count_for_calc_y - y_a_asks_num[ai]
                    else:
                        x_part_1_y_count = x_part_1_y_count + x_part_1_a_count_for_calc_y * y_a_asks_price[ai]
                        break
            else:
                for ai in part:
                    x_part_1_y_count = x_part_1_y_count + y_a_asks_num[ai] * y_a_asks_price[ai]
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
                x_part_2_y_count_ax = x_part_2_y_count_ax + y_b_bids_num[ai] * y_b_bids_price[ai]
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
                    if x_part_1_y_count_for_calc - y_b_bids_num[ai] * y_b_bids_price[ai] > 0:
                        x_part_2_b_count = x_part_2_b_count + y_b_bids_num[ai]
                        x_part_1_y_count_for_calc = x_part_1_y_count_for_calc - y_b_bids_num[ai] * \
                                                                                y_b_bids_price[ai]
                    else:
                        x_part_2_b_count = x_part_2_b_count + x_part_1_y_count_for_calc / y_b_bids_price[ai]
                        break
            else:
                # 如果part3的y 小于part2y 说明 已part3为主 b的num直接累加即可
                for ai in part:
                    x_part_2_b_count = x_part_2_b_count + y_b_bids_num[ai]
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
                x_part_3_b_count = x_part_3_b_count + x_b_asks_num[ai]

            if (x_part_2_b_count < x_part_3_b_count):
                x_part_3_b_count = x_part_2_b_count
            # 算 x_end
            x_part_3_b_count_for_calc = x_part_3_b_count
            for ai in part:
                if x_part_3_b_count_for_calc - x_b_asks_num[ai] > 0:
                    x_end = x_end + x_b_asks_num[ai] * x_b_asks_price[ai]
                    x_part_3_b_count_for_calc = x_part_3_b_count_for_calc - x_b_asks_num[ai]
                else:
                    x_end = x_end + x_part_3_b_count_for_calc * x_b_asks_price[ai]
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
    x_part_2_b_count_for_calc = x_part_3_b_count
    for ai in path_list[2]:
        if x_part_2_b_count_for_calc - y_b_bids_num[ai] > 0:
            x_part_2_y_count_begin = x_part_2_y_count + y_b_bids_num[ai] * y_b_bids_price[ai]
            x_part_2_b_count_for_calc = x_part_2_b_count_for_calc - y_b_bids_num[ai]
        else:
            x_part_2_y_count_begin = x_part_2_y_count + x_part_2_b_count_for_calc * y_b_bids_price[ai]
            break

    # x_part_2_y_count求出来了 求 x_part_1_a_count
    # 卖(hrs->btc) ask
    # btc count
    # 上一步算出了 a 货币的数量
    # "asks":[[0.000876,8.1],[0.000877,2],[0.000879,10],[0.00088,1],[0.000881,1]]
    #"asks": [[0.000876, 88.1], [0.000877, 2], [0.000879, 25], [0.00088, 10.78], [0.000881, 2]]
    # y_a_asks_price
    x_part_1_y_count_for_calc = x_part_2_y_count_begin
    for ai in path_list[1]:
        if x_part_1_y_count_for_calc - y_a_asks_price[ai] * y_a_asks_num[ai] > 0:
            x_part_1_a_count_begin = x_part_1_a_count_begin + y_a_asks_num[ai]
            x_part_1_y_count_for_calc = x_part_1_y_count_for_calc - y_a_asks_price[ai] * y_a_asks_num[ai]
        else:
            x_part_1_a_count_begin = x_part_1_a_count_begin + x_part_1_y_count_for_calc / y_a_asks_price[ai]
            break;

    # 最后一步算x起
    # part1 的 a 已经反推出来 最后反推x起
    # x_part_1_a_count_begin
    # price * num
    # 买(eth->hrs) bid
    # hrs count
    # "bids":[[0.01105,2.2376],[0.010981,16.95],[0.010979,34],[0.010978,82.2761],[0.010972,0.0007]]
    x_part_0_a_count_for_calc = x_part_1_a_count_begin
    for ai in path_list[0]:
        if x_part_0_a_count_for_calc - x_a_bids_num[ai] > 0:
            x_part_0_a_count_begin = x_part_0_a_count_begin + x_a_bids_num[ai] * x_a_bids_price[ai]
            x_part_0_a_count_for_calc = x_part_0_a_count_for_calc - x_a_bids_num[ai]
        else:
            x_part_0_a_count_begin = x_part_0_a_count_begin + x_part_0_a_count_for_calc * x_a_bids_price[ai]
            break

    return x_part_0_a_count_begin, x_end,x_end*0.998*0.998*0.998*0.998,x_part_0_a_count_begin < x_end*0.998*0.998*0.998*0.998
