# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import pymysql
from sports_subscribe_scrape.config import *

class SportsSubscribeScrapePipeline:
    con = pymysql.connect(host=db_host, user=db_user, password=db_password, database=database)
    cur = con.cursor()

    def process_item(self, item, spider):
        return item
