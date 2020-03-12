# encoding: utf-8

import pymysql
import sys

class OpMysql(object):
    # 连接ali云数据库，使用云数据库外网地址
    def __init__(self, host, user, password, database):
        try:
            self.conn = pymysql.connect(host=host, user=user, password=password, database=database)
            self.cur = self.conn.cursor()
        except pymysql.Error as e:
            print('connect mysql error')
            sys.exit(0)

    def select_one(self, query, params=None):
        try:
            result = self.cur.execute(query, params)
            if result > 1:
                print('找到多条数据')
            elif result == 1:
                return self.cur.fetchone()
            else:
                # 查询到的结果为0
                print('找不到符合条件的数据')
        except BaseException as e:
            return '001'

    # 删除内部账号二次验证名单，返回None
    def internal_account_delete_two_step_verification(self, user_id):
        result = self.cur.execute('DELETE FROM two_step_verification WHERE user_id=%s', (user_id, ))
        if self.cur.rowcount == 1:
            self.conn.commit()

    # 内部账号：删除fishID和内部账号ID的映射关系
    def delete_relation_internal_fish(self, fish_id):
        result = self.cur.execute('DELETE FROM relation_internal_fish WHERE fish_id=%s', (fish_id, ))
        if self.cur.rowcount == 1:
            self.conn.commit()

if __name__ == '__main__':
    # 连接dev环境account库
    opmysql_account = OpMysql(host='rm-bp173j25673ah67z8ko.mysql.rds.aliyuncs.com', user='TestDep', password='4Ehp1ndpfnlN9D0qvg4SZuig', database='account')
    data = opmysql_account.select_one("SELECT * from basic_auth where user_id=%s", (1000002450, ))
    print(data)

    # 连接dev环境internal_account库
    opmysql_internal_account = OpMysql(host='rm-bp1udh67050zd1n0b115.mysql.rds.aliyuncs.com', user='TestDep', password='4Ehp1ndpfnlN9D0qvg4SZuig', database='internal_account')
    data = opmysql_internal_account.internal_account_delete_two_step_verification(438)
    print(data)