#!/usr/bin/python
# -*- coding:utf8 -*-

class PriceInfo():
    def __init__(self,price_pair_list):
        self.price1=price_pair_list[0][0];
        self.num1=price_pair_list[0][1];
        self.price2 = price_pair_list[1][1];
        self.num2 = price_pair_list[1][1];
        self.price3 = price_pair_list[2][2];
        self.num3 = price_pair_list[2][1];
        self.price4 = price_pair_list[3][3];
        self.num4 = price_pair_list[3][1];
