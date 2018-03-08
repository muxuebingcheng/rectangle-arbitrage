#!/usr/bin/python
# -*- coding:utf8 -*-

#根据数据生成路径 eth -> A ; A - > btc ; btc -> B ; B-> etc
#例子:
#        卖           买           卖         买
#    etc -> hsr ; hsr -> btc ; btc -> gnt; gnt ->etc

#原始数据类型（只取前5价格，升序???）
# etc -> hsr bids
# 降序 [[0.010979, 34], [0.010978, 82.2761], [0.010972, 0.0007], [0.010936, 182.473], [0.010922, 86.7123]]
# hsr -> btc asks
# 降序 [[0.000879, 25], [0.00088, 10.78], [0.000881, 2], [0.000886, 2], [0.000887, 1086.8]]
# btc -> gnt
# 降序 [[3.906e-05, 1035], [3.904e-05, 1332], [3.888e-05, 2618], [3.879e-05, 828], [3.875e-05, 2429]]
# gnt ->etc
# 降序 [[0.009411, 42.479], [0.00943, 25.8621], [0.009463, 74], [0.009464, 74], [0.00948, 148]]

#函数根据传入的值进行生成路径
#输入格式
def get_all_subsets(number):
    index = range(number)
    result = []
    for i in range(2**number):
	item = []
	for j in range(number):
	    if(i>>j)%2==1:
		item.append(index[j])
	if len(item)==0:
	    continue
	result.append(item)
    return result

def gen_path_info(source_data):
    if len(source_data)==0:
	return
    #choose all two currencies from the source_data
    all_index = range(len(source_data))
    all_pairs = []
    for item in itertools.permutations(all_index,2):
	all_pairs.append(item)
    path = []
    for pair in all_pairs:
	a_info = source_data[pair[0]]
	b_info = source_data[pair[1]]
	path_eth_a = []
	path_a_btc = []
	path_btc_b = []
	path_b_eth = []
	#TODO
    return


