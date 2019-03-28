# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb
import MySQLdb.cursors

from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.conn = MySQLdb.connect('192.168.198.129','root','Liuxh520','articleSpider',charset = "utf8",use_unicode = True)
        self.cursor = self.conn.cursor()

    def process_item(self,item,spider):
        insert_sql = """
            insert into article(title,url,create_date,fav_nums,url_object_id,comment_nums,praise_nums,tags)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql,(item["title"], item["url"],item["create_date"],item["favour_nums"], item["url_object_id"], item["comment_nums"], item["praise_nums"],item["tags"]))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        dbparm = dict(
            host=settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8mb4',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True
        )


        dbpool = adbapi.ConnectionPool("MySQLdb",**dbparm)

        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert,item)
        query.addErrback(self.handle_error,item,spider)

    def handle_error(self,failure,item,spider):
        #处理异步异常
        print(failure)

    def do_insert(self, cursor, item):
        insert_sql = """
                    insert into article(title, url_object_id,url, create_date,comment_nums,praise_nums,fav_nums,content,tags)
                    VALUES (%s, %s,%s,%s,%s,%s,%s,%s,%s)
                """
        cursor.execute(insert_sql, (
        item["title"], item["url_object_id"],item["url"], item["create_date"],item["comment_nums"],item["praise_nums"],item["favour_nums"],item["content"],item["tags"]))




class JsonWithEncodingPipeline(object):
    #zidingyi daochu
    def __init__(self):
        self.file = codecs.open('article.json','w',encoding="utf-8")

    def process_item(self,item,spider):
        lines = json.dumps(dict(item),ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self,spider):
        self.file.close()

class JsonExporterPipeline(object):
    #调用scrapy提供的json_export
    def __init__(self):
        self.file = open('articleexport.json','wb')
        self.exporter = JsonItemExporter(self.file,encoding = "utf-8",ensure_ascii = False)
        self.exporter.start_exporting()

    def closer_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item