#!/usr/bin/python
# -*- coding:utf8 -*-

import json
import entity.CurrencyPairInfo

def format_receive_data(source_data):
     data = json.loads(source_data)
     data = data['data'];
     #eth - a | a - btc | btc - b | b - eth
     #data =['blz' ,' mtn' ,' ht' ,' zla' ,' mds' ,' nas' ,' swftc' ,' let' ,' pay' ]
     currency_pair_info_list=[]

     #排除不完整货币对
     currency_list=filter_currency_pair(data)
     #data_info {u'symbol': u'hsr-eth', u'bids': [[0.01105, 2.2376], [0.010981, 16.95], [0.010979, 34], [0.010978, 82.2761], [0.010972, 0.0007], [0.010936, 182.473], [0.010922, 86.7123]], u'asks': [[0.011123, 34], [0.011124, 182.473], [0.01116, 34], [0.011168, 70.8], [0.011173, 56.52], [0.011253, 68], [0.011254, 88.9182]]}
     #创建两条边
     two_edge_list=create_two_edge_list(data,currency_list)
     return two_edge_list

def format_send_data(source_data):
    return source_data

def filter_currency_pair(data):
    eth_pair_array={}
    btc_pair_array={}
    for currency_pair_info in data:
        if(currency_pair_info['symbol']=='eth-btc'):
            continue
        #hsr-etc or hsr-btc
        symbol=currency_pair_info['symbol']
        currency=symbol.split('-')[0]
        key=symbol.split('-')[1]
        if(key == 'eth'):
            eth_pair_array[currency]=currency
        elif(key == 'btc'):
            btc_pair_array[currency]=currency
    #eth btc共有货币
    currency_list=[]
    for currency in eth_pair_array:
        if(btc_pair_array.has_key(currency)):
            currency_list.append(currency);
    return currency_list

def create_two_edge_list(data,currency_list):
    data_dic={}
    for data_info in data:
        data_dic[data_info['symbol']]=data_info
    two_edge_list=[]
    for currency in currency_list:
        eth_bids = data_dic[currency+'-eth']['bids'][0:5]
        eth_asks = data_dic[currency+'-eth']['asks'][0:5]
        btc_bids = data_dic[currency+'-btc']['bids'][0:5]
        btc_asks = data_dic[currency+'-btc']['asks'][0:5]
        cp = entity.CurrencyPairInfo.TowEdgesInfo(currency,eth_bids,eth_asks,btc_bids,btc_asks)
        two_edge_list.append(cp)
    return two_edge_list


