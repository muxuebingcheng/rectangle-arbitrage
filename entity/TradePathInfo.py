#!/usr/bin/python
# -*- coding:utf8 -*-

class XInitNumInfo:
    x_init=0
    def __init__(self,digiccy_a,digiccy_b,price_info_1,price_info_2,price_info_3,price_info_4):
        self.digiccy_a=digiccy_a
        self.digiccy_b=digiccy_b
        self.part1_info=self.calc_part_value(price_info_1)
        self.part2_info=self.calc_part_value(price_info_2)
        self.part3_info=self.calc_part_value(price_info_3)
        self.part4_info=self.calc_part_value(price_info_4)

    def calc_part_value(slef,price_info):
        return