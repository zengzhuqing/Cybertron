#-*- coding:utf-8 -*-

import MySQLdb

import config

def mysql_con(config, cur_class=None):
    con = MySQLdb.connect(**config)
    cur = con.cursor(cur_class)
    return con, cur

def get_bz_con(cur_class=None):
    return mysql_con(config.bz_config, cur_class)

if __name__ == '__main__':
    print get_bz_con()
   # etl_con()
