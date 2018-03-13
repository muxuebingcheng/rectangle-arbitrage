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

def filter_paths(paths):
    #TODO
    #this part maybe has bugs,and this code part can only be used in this scenario
    result = []
    for item in paths:
        if len(item)==1:
            result.append(item)
        elif len(item)==2:
            if (item[1]-item[0])==1:
                result.append(item)
        else:
            diff = set()
            for i in range(len(item)-1):
                diff.add(item[i+1]-item[i])
            if len(diff)==1 and list(diff)[0]==1:
                result.append(item)
    return result

def full_paths():
    out_file = open('result.txt','w')
    path1 = filter_paths(get_all_subsets(1,5))
    path2 = filter_paths(get_all_subsets(2,5))
    path3 = filter_paths(get_all_subsets(3,5))
    path4 = filter_paths(get_all_subsets(4,5))
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
    #TODO
    #result = filter_paths(paths)
    dump(new_r)

def dump(result):
    out_file = open("result.txt","w")
    for item in result:
        out_file.write('->'.join(str(v) for v in item)+"\n")
    out_file.close()

if __name__ == "__main__":
    number = 3
    group = 1
    #print get_all_subsets(number,group)
    full_paths()
