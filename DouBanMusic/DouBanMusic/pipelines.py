# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import requests
from .items import DoubanUserItem
from .items import ProxyItem
from .items import UserMusicCollectItem
from .items import UserMusicWishItem
from .items import UserMusicDoItem
from .items import MusicInfoItem
from .items import SongInfoItem
from .items import UpdateMusicInfoItem
from scrapy.exceptions import DropItem


class DoubanmusicPipeline(object):
    def process_item(self, item, spider):
        return item


class MysqlPipeline(object):
    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_passwd, mysql_charset):
        self.host = mysql_host
        self.port = mysql_port
        self.db = mysql_db
        self.user = mysql_user
        self.passwd = mysql_passwd
        self.charset = mysql_charset

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_passwd=crawler.settings.get('MYSQL_PASSWD'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET')
        )

    def open_spider(self, spider):
        spider.myPipeline = self
        self.connect = pymysql.connect(
            host=self.host,
            port=self.port,
            db=self.db,
            user=self.user,
            passwd=self.passwd,
            charset=self.charset,
            use_unicode=True
        )
        self.cursor = self.connect.cursor()

    def close_spider(self, spider):
        self.connect.close()

    def process_item(self, item, spider):
        if isinstance(item, DoubanUserItem):
            if item.get('doubanid') is None:
                raise DropItem('用户已注销')
            else:
                sql = 'insert into Users(userid, name, href) values (%s,%s,%s)'
                self.cursor.execute(sql, (item['doubanid'], item['name'], item['href']))
                self.connect.commit()
                return item
        elif isinstance(item, ProxyItem):
            if item['type'] == 'http':
                raise DropItem('Not HTTPS IP ADDRESS. DROPED.')
            else:
                # 判断地址有效性
                proxy = item['type'] + '://' + item['ip'] + ':' + item['port']
                proxies = {item['type']: proxy}
                try:
                    test_proxy = requests.get(url='https://httpbin.org/get', proxies=proxies, timeout=0.001)
                except Exception as e:
                    raise DropItem('This Proxy IP is dead, drop it. %s' % proxy)
                sql = 'insert into ProxyPool(ip,port,type) values (%s,%s,%s)'
                if item['type'] == 'HTTP':
                    item['type'] = 0
                else:
                    item['type'] = 1
                self.cursor.execute(sql, (item['ip'], item['port'], item['type']))
                self.connect.commit()
                return item
        elif isinstance(item, UserMusicCollectItem):
            sql = 'insert ignore into UserMusicCollect(userid,itemid,rating,date) values (%s,%s,%s,%s)'
            self.cursor.execute(sql, (item['userid'], item['itemid'], item['rating'], item['date']))
            self.connect.commit()
            return item
        elif isinstance(item, UserMusicDoItem):
            sql = 'insert ignore into UserMusicDO(userid,itemid,rating,date) values (%s,%s,%s,%s)'
            self.cursor.execute(sql, (item['userid'], item['itemid'], item['rating'], item['date']))
            self.connect.commit()
            return item
        elif isinstance(item, UserMusicWishItem):
            sql = 'insert ignore into UserMusicWish(userid,itemid,rating,date) values (%s,%s,%s,%s)'
            self.cursor.execute(sql, (item['userid'], item['itemid'], item['rating'], item['date']))
            self.connect.commit()
            return item
        elif isinstance(item, MusicInfoItem):
            sql = 'insert ignore into MusicInfo(itemid,name,content) values (%s,%s,%s)'
            self.cursor.execute(sql, (
                item['itemid'], item['name'], item['content']))
            self.connect.commit()
            return item
        elif isinstance(item, SongInfoItem):
            sql = 'insert ignore into SongInfo(songname,itemid) values (%s,%s)'
            self.cursor.execute(sql, (item['songname'], item['itemid']))
            self.connect.commit()
        elif isinstance(item, UpdateMusicInfoItem):
            # if item['style'] == None:
            #     item['style'] = 'NULL'
            # if item['player'] == None:
            #     item['player'] = 'NULL'
            # sql = "Update MusicInfo Set style='" + item['style'] + "',player='" + item['player'] + "' where itemid='" + \
            #       str(item['itemid']) + "'"
            sql = 'update MusicInfo Set style=%s,player=%s where itemid=%s'
            self.cursor.execute(sql, (item['style'] or None, item['player'] or None, item['itemid']))
            self.connect.commit()

    def get_all_users(self):
        sql = 'select userid from Users'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results

    def get_all_musics(self):
        sql = 'select itemid from MusicInfo'
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return results
    # def test_proxy(self,):
