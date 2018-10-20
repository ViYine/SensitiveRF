import json
import sqlite3
import logging
import csv

def jsonread(filename):
    try:
        res = json.loads(open(filename,encoding='utf-8').read())
        return res
    except Exception as e:
        logging.error(e)
        print("数据指标配置文件读入错误，请检查指标配置文件并重试")
        return None
def csvread(filename):
    try:
        res = csv.reader(open(filename))
        return res
    except Exception as e:
        logging.error(e)
        print("指标的评估结果文件读入错误，请检查文件并重试")
        return None
def jsonwrite(dir, filename):
    datastr = json.dumps(dir, sort_keys=True, indent=2)
    outfile = open(filename, 'w')
    outfile.write(datastr)