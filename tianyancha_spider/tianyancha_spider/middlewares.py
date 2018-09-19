# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.http import HtmlResponse
import time, random

class TianyanchaSpiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)



class RandomUserAgentMiddlware(object):
    #随机更换user-agent
    def __init__(self, crawler):
        super(RandomUserAgentMiddlware, self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get("RANDOM_UA_TYPE", "random")

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def process_request(self, request, spider):
        def get_ua():
            return getattr(self.ua, self.ua_type)

        request.headers.setdefault('User-Agent', get_ua())



class JavaScriptMiddleware(object):
    def process_request(self, request, spider):
        spider.browser.get(request.url)
        time.sleep(10)
        content = spider.browser.page_source
        return HtmlResponse(request.url, encoding='utf-8', body=content, request=request)

class JSPageMiddleware(object):
    #通过chrome 动态访问
    def process_request(self,request,spider):
        spider.browser.get(request.url)
        spider.browser.execute_script("var q=document.documentElement.scrollTop=10000")
        time.sleep(random.randint(3, 8))
        print("访问：{0}".format(request.url))

        if "login" in request.url:

            spider.browser.find_element_by_xpath('//div[contains(@class,"modulein modulein1")]\
                                 //div[@class="pb30 position-rel"]//input').send_keys('xxxxxxxx')
            time.sleep(random.randint(2, 5))

            spider.browser.find_element_by_xpath('//div[contains(@class,"modulein modulein1")]\
                                 //div[@class="pb40 position-rel"]//input').send_keys('xxxxxxx')
            time.sleep(random.randint(1, 3))
            spider.browser.find_element_by_xpath('//div[contains(@class,"modulein modulein1")]'
                                        '//div[@onclick="loginByPhone(event);"]').click()
            time.sleep(random.randint(1, 4))

            return HtmlResponse(url=spider.browser.current_url,body=spider.browser.page_source,encoding="utf-8")

        else:
            time.sleep(random.randint(2, 5))
            return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source,request=request,encoding="utf-8")
            # return request

