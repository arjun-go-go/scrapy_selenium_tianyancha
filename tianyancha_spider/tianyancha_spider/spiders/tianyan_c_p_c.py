# -*- coding: utf-8 -*-
# author: arjun
# @Time: 18-5-10 上午2:21

import csv
import datetime
import scrapy
import time
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from scrapy import signals
from copy import deepcopy



class TianyanCPCSpider(scrapy.Spider):
    name = 'tianyan_c_p_c'
    allowed_domains = ['tianyancha.com']
    start_urls = ['https://www.tianyancha.com/login']

    #无头浏览
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        self.browser = webdriver.Chrome(chrome_options=chrome_options)
        super(TianyanCPCSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    #爬虫关闭时关闭浏览器
    def spider_closed(self, spider):
        print("spider closed")
        self.browser.quit()

    def parse(self, response):
        company_list = csv.reader(open('example.csv', 'r'))
        for i in company_list:
            i = i[0]
            urls = response.url + "search?key={0}".format(i)
            yield scrapy.Request(urls
                                 , callback=self.parse_company
                                 , meta={"i": i})

    def parse_company(self, response):
        i = response.meta["i"]
        divs = response.xpath("//div[@class='result-list']/div")
        list = []
        for div in divs:
            temp = {}
            temp["company_url"] = div.xpath(".//div[@class='header']/a/@href").extract_first()
            titles = div.xpath(".//div[@class='match text-ellipsis']/span/text()").extract_first()
            if titles is not None and "历史名称" in titles:
                temp["old_name"] = div.xpath(".//div[@class='match text-ellipsis']/span[2]/em/text()").extract_first()
            else:
                temp["old_name"] = ""
            names = div.xpath(".//div[@class='header']/a//text()").extract()
            if len(names) > 0:
                temp["company_name"] = "".join(names)
            list.append(temp)
        for li in list:
            if li["company_name"] == i or li["old_name"] == i:
                company_url = li["company_url"]
                yield scrapy.Request(company_url
                                     , callback=self.company_detail
                                     , meta={"i": i})


    """公司详情信息获取"""
    def company_detail(self, response):
        i = response.meta["i"]
        item = {}
        item["createtime"] = int(time.time())
        company = response.xpath(
            "//div[@class='content']/div[@class='header']/h1/text()").extract_first()
        if company != i:
            item["company"] = i
        else:
            item["company"] = company
        """主要人员信息"""
        staff_count = response.xpath(
            "//div[@id='_container_staff']//tr")[1:]
        if not staff_count:
            staff_count = response.xpath(
                "//div[@id='_container_holder']//tr")[1:]

        for staff in staff_count:
            item["person_name"] = staff.xpath("./td[2]/div[@class='text-image-human']/a[1]/text()").extract_first()
            item["position"] = staff.xpath("./td[3]/span/text()").extract_first()
            item["preson_href"] = staff.xpath("./td[2]/div[@class='text-image-human']/a[2]/@href").extract_first()
            yield scrapy.Request(item["preson_href"]
                                 ,callback=self.main_person_detail
                                 ,meta={"item": deepcopy(item)})

    """主要人员的信息请求链接"""
    def main_person_detail(self, response):
        item = deepcopy(response.meta["item"])
        ts = response.xpath("//div[@id='_container_sygs']//table[@class='table']/tbody/tr")
        for t in ts:
            item["com_name"] = t.xpath("./td[2]//tr/td[2]/a/text()").extract_first()
            m_position = t.xpath("./td[6]/text()").extract_first()
            if m_position is not None:
                item["job"] = m_position
            else:
                item["job"] = "股东"
            yield item

