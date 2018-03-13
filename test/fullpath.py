#!/usr/bin/env python
#coding:utf-8
import itertools

def get_all_subsets(group,number=5):
    base = group*10
    index = []
    for i in range(number):
        index.append(base+i)
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

def full_permutations(yourlist,number=2):
    #yourlist is your list which you want to product permutations with the set
    all_permutations = []
    for item in itertools.permutations(yourlist,number):
        all_permutations.append(item)
    return all_permutations

def get_product(g1,g2):
    result = []
    for item in itertools.product(g1,g2):
        result.append(item)
    return result

def test():
    out_file = open('result.txt','w')
    path1 = get_all_subsets(1,5)
    path2 = get_all_subsets(2,5)
    path3 = get_all_subsets(3,5)
    path4 = get_all_subsets(4,5)
    r1 = get_product(path1,path2)
    r2 = get_product(path3,path4)
    #r = get_product(r1,r2)
    new_r1 = []
    for item in r1:
        new_list = item[0]+item[1]
        new_r1.append(new_list)
    #print new_r1
    new_r2 = []
    for item in r2:
        new_list = item[0]+item[1]
        new_r2.append(new_list)
    #print new_r2
    r = get_product(new_r1,new_r2)
    new_r = []
    for item in r:
        new_list = item[0]+item[1]
        new_r.append(new_list)
    for item in new_r:
        out_file.write('->'.join(str(v) for v in item)+"\n")

def full_paths():
    path1 = get_all_subsets(1)
    path2 = get_all_subsets(2)
    path3 = get_all_subsets(3)
    path4 = get_all_subsets(4)
    result1 = get_product(path1,path2)
    result2 = get_product(path3,path4)
    result3 = get_product(result1,result2)
    '''
    print result3[0]
    print result3[0][0]
    print result3[0][1]
    print result3[0][0][0][0]
    print result3[0][0][1][0]
    print result3[0][1][0][0]
    print result3[0][1][1][0]
    '''
    result = []
    for item in result3:
        r1 = item[0][0][0]
        r2 = item[0][1][0]
        r3 = item[1][0][0]
        r4 = item[1][1][0]
        result.append([r1,r2,r3,r4])
    return result

if __name__ == "__main__":
    number = 3
    group = 1
    #print get_all_subsets(number,group)
    test()
