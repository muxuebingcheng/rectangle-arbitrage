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

def get_paths_from_local_data(myfile):
    data = open(myfile)
    paths = []
    for line in data.readlines():
	data = line.strip().split(",")
	path1 = []
	path2 = []
	path3 = []
	path4 = []
	for item in data:
	    if int(item)<20:#group1
		path1.append(int(item)%10)
	    elif int(item)>=20 and int(item)<30:#group2
		path2.append(int(item)%20)
	    elif int(item)>=30 and int(item)<40:#group3
		path3.append(int(item)%30)
	    else:
		path4.append(int(item)%40)
	path = []
	path.append(path1)
	path.append(path2)
	path.append(path3)
	path.append(path4)
	paths.append(path)
    return paths


#函数根据传入的值进行生成路径
#输入格式
import itertools
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
        path_data = []
    for pair in all_pairs:
        a_info = source_data[pair[0]]
        b_info = source_data[pair[1]]
    ###########produce four module exchange infos############
    #module1:etc->a
    #module2:a->btc
    #module3:btc->b
    #module4:b->eth
    #a_info data structure
    #a_info.eth_bids:[[ratio,count],[],[],[],[]]#the length of this data is no more than 5
    #a_info.eth_asks:[[ratio,count],[],[],[],[]]#the length of this data is no more than 5
    #a_info.btc_bids:[[ratio,count],[],[],[],[]]#the length of this data is no more than 5
    #a_info.btc_asks:[[ratio,count],[],[],[],[]]#the length of this data is no more than 5
    exchange_module1 = a_info.eth_bids#use a.eth_bids
    exchange_module2 = a_info.btc_asks#use a.btc_asks
    exchange_module3 = b_info.btc_bids#use b.btc_bids
    exchange_module4 = b_info.eth_asks#use b.eth_asks
    ###################################################################

    ###########produce module path using cartesian product##########
    path_module1_index = get_all_subsets(len(exchange_module1))#this part can be optimized, because the data is ordered, and now the result omit the order
    path_module2_index = get_all_subsets(len(exchange_module2))
    path_module3_index = get_all_subsets(len(exchange_module3))
    path_module4_index = get_all_subsets(len(exchange_module4))

    #step1:produce path from module1 to module2
    path_step1 = []
    for path1 in path_module1_index:
        for path2 in path_module2_index:
            path_step1.append([path1,path2])
    #step2:produce path from step1(module1->module2) to module3
    path_step2 = []
    for path1 in path_step1:
        for path3 in path_module3_index:
            path_step2.append(path1.append(path3))
    #step3:produce path from step2(module1->module2->module3) to module4
    path_step3 = []
    for path2 in path_step2:
        for path4 in path_module4_index:
            path_step3.append(path2.append(path4))
    #the final path
    paths = path_step3
    #note:paths is a list, each element is an inner list which has four items. The four item covers four module paths
    #example:[path1,path2,path3,path4],path1=[0,1],path2=[1,2],path3=[1,3],path4=[1,2,3]
    #produce the final data
    for path in paths:
        path_module1 = path[0]
        path_module2 = path[1]
        path_module3 = path[2]
        path_module4 = path[3]
        path1_data = []
        path2_data = []
        path3_data = []
        path4_data = []
        for index in path_module1:
            path1_data.append(exchange_module1[index])
        for index in path_module2:
            path2_data.append(exchange_module2[index])
        for index in path_module3:
            path3_data.append(exchange_module3[index])
        for index in path_module4:
            path4_data.append(exchange_module4[index])
        path_data.append([path1_data,path2_data,path3_data,path4_data])
    return path_data
