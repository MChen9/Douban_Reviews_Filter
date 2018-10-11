# -*- coding: UTF-8 -*-
import MySQLdb
from datetime import date


def requestsql(cid, username, moviecode, votes, ratestars, Date, content, addtime):
    db = MySQLdb.connect(host='localhost', user='root', passwd='12345droeeN', db='testdb', charset='utf8')
    cursor = db.cursor()

    sql = "INSERT IGNORE INTO testdb.Douban_Movie_Ready_Player_One(cid, user_name, movie_code, \
           votes, rate_stars, date, content, add_time) \
           VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % \
          (cid, username, moviecode, votes, ratestars, Date, content, addtime)

    try:
        # execute sql
        cursor.execute(sql)
        # submit to database
        db.commit()
    except:
        # Rollback in case there is any error
        db.rollback()

    db.close()


if __name__ == '__main__':
    addtime = int(''.join(str(date.today()).split('-')))
    cid, username, code, votes, ratestars, Date, content, addtime = '222', 'ssss', '222', '34', '5', '20180901', 'eeee', addtime
    requestsql(cid, username, code, votes, ratestars, Date, content, addtime)
