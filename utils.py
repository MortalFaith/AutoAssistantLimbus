import os
import json

def cal_StarLight():
    rest = int(input("请输入休息补给的星光数："))
    avail_StarLight = 62 + 1.86 * rest
    print(f"本局可以放心使用的星光数量为： {avail_StarLight} ")