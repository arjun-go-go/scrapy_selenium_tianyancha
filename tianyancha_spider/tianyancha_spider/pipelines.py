# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

from .settings import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME


class TianyanchaSpiderPipeline(object):
    def process_item(self, item, spider):
        return item



class MysqlPipeline(object):
    # 采用同步的机制写入mysql
    def __init__(self):
        self.conn = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DBNAME, charset="utf8")
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
                      insert into tianyan_c_c_c (company,fir_relation,company_name,sec_relation,com_name,createtime
                        ) VALUES (%s, %s, %s, %s, %s, %s)


                    """
        self.cursor.execute(insert_sql, (item["company"], item["fir_relation"]
                                         , item["company_name"], item["sec_relation"]
                                         , item["com_name"],item["createtime"]
                                         ))
        self.conn.commit()

