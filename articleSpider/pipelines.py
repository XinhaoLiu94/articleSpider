# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import codecs
import json
import MySQLdb

from scrapy.exporters import JsonItemExporter

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