# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
# from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.utils.response import response_status_message
import random
import pymysql
import requests
import base64
import time
from twisted.internet.error import TimeoutError
from .spiders.SongList import SonglistSpider


class DoubanmusicSpiderMiddleware(object):
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


class DoubanmusicDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        # request.meta['proxy']='http://127.0.0.1:1087'
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class MyUserAgentMiddleware(UserAgentMiddleware):
    '''
    设置User-Agent
    '''

    def __init__(self, user_agent):
        super().__init__(user_agent)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            user_agent=crawler.settings.get('USER_AGENTS_LIST')
        )

    def process_request(self, request, spider):
        agent = random.choice(self.user_agent)
        request.headers[
            'User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'


class MySqlProxyMiddleware(object):
    def __init__(self, mysql_host, mysql_port, mysql_db, mysql_user, mysql_passwd, mysql_charset):
        self.host = mysql_host
        self.port = mysql_port
        self.db = mysql_db
        self.user = mysql_user
        self.passwd = mysql_passwd
        self.charset = mysql_charset

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(
            mysql_host=crawler.settings.get('MYSQL_HOST'),
            mysql_port=crawler.settings.get('MYSQL_PORT'),
            mysql_db=crawler.settings.get('MYSQL_DB'),
            mysql_user=crawler.settings.get('MYSQL_USER'),
            mysql_passwd=crawler.settings.get('MYSQL_PASSWD'),
            mysql_charset=crawler.settings.get('MYSQL_CHARSET')
        )
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(s.spider_closed, signal=signals.spider_closed)
        return s

    def spider_opened(self, spider):
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
        self.cursor.execute('select * from ProxyPool')
        rowlist = self.cursor.fetchall()
        num = 1
        self.proxypool = []
        for (id, ip, port, Type) in rowlist:
            Type = ('https' if (Type == b'\x01') else 'http')
            proxy = Type + '://' + ip + ':' + port
            proxies = {'https': proxy}
            try:
                test_proxy = requests.get(url='https://httpbin.org/get', proxies=proxies, timeout=0.001)
            except Exception as e:
                spider.logger.info('This Proxy IP is dead, drop it. %s' % proxy)
                self.cursor.execute('delete from ProxyPool where id=' + str(id))
                continue
            spider.logger.info('%d' % num)
            num += 1
            self.proxypool.append(proxy)
        self.connect.commit()
        spider.logger.info('ProxyPool prepared.')

    def process_request(self, request, spider):
        request.meta['proxy'] = random.choice(self.proxypool)

    def spider_closed(self):
        self.connect.close()

    def process_exception(self, request, exception, spider):
        if type(exception) is IndexError:
            return request
        else:
            print(exception)


class AbuyunProxyMiddleware(object):
    def __init__(self, proxyHost, proxyPort, proxyUser, proxyPwd):
        self.proxyHost = proxyHost
        self.proxyPort = proxyPort
        self.proxyUser = proxyUser
        self.proxyPwd = proxyPwd
        self.proxyPool = ()

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            proxyHost=crawler.settings.get('PROXYHOST'),
            proxyPort=crawler.settings.get('PROXYPORT'),
            proxyUser=crawler.settings.get('PROXYUSER'),
            proxyPwd=crawler.settings.get('PROXYPWD')
        )

    def process_request(self, request, spider):
        proxyServer = self.proxyHost + ':' + self.proxyPort
        proxyAuth = "Basic " + base64.urlsafe_b64encode(
            bytes((self.proxyUser + ":" + self.proxyPwd), "ascii")).decode("utf8")
        request.meta['proxy'] = proxyServer
        request.headers['Proxy-Authorization'] = proxyAuth


class PadailiProxyMiddleware(object):
    def __init__(self, api):
        self.api = api

    @classmethod
    def from_crawler(cls, crawler):
        s = cls(api=crawler.settings.get('PADAILIAPI'))
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def spider_opened(self, spider):
        self.make_proxypool(spider)

    def process_request(self, request, spider):
        proxyServer = random.choice(self.proxyPool)
        while len(self.proxyPool) > 0:
            proxies = {'https': proxyServer}
            try:
                test_proxy = requests.get(url='https://httpbin.org/get', proxies=proxies, timeout=1)
                break
            except Exception as e:
                spider.logger.info(e)
                spider.logger.info('This Proxy IP is dead, drop it. %s' % proxyServer)
                self.proxyPool.remove(proxyServer)
                if not self.proxyPool:
                    self.make_proxypool(spider)
                proxyServer = random.choice(self.proxyPool)
                continue
        request.meta['proxy'] = proxyServer

    # def process_exception(self, request, exception, spider):
    #     # Called when a download handler or a process_request()
    #     # (from other downloader middleware) raises an exception.
    #
    #     # Must either:
    #     # - return None: continue processing this exception
    #     # - return a Response object: stops process_exception() chain
    #     # - return a Request object: stops process_exception() chain
    #     pass

    def make_proxypool(self, spider):
        spider.logger.info('Start to make proxypool through Padaili API...')
        proxypool = []
        proxylist = requests.get(
            'http://www.padaili.com/proxyapi.php?apikey=b24d1c5c457639d59931eb0eff5a99ee&num=100&type=1,2&xiangying=1&order=jiance')
        proxylist = proxylist.text.strip('\n').split('</br>')
        proxylist.remove('')
        for proxy in proxylist:
            proxies = {'https': proxy}
            try:
                test_proxy = requests.get(url='https://httpbin.org/get', proxies=proxies, timeout=1)
            except Exception as e:
                spider.logger.info(e)
                spider.logger.info('This Proxy IP is dead, drop it. %s' % proxy)
                continue
            proxypool.append(proxy)
        proxypool = set(proxypool)
        self.proxyPool = list(proxypool)
        spider.logger.info('ProxyPool has prepared. Total num is %d' % len(self.proxyPool))


class LocalRetryMiddleware(RetryMiddleware):
    def process_response(self, request, response, spider):
        if request.meta.get('dont_retry', False):
            return response
        if response.status in self.retry_http_codes:
            reason = response_status_message(response.status)
            if response.status == 404 and isinstance(spider, SonglistSpider):
                spider.current_music += 1
                next_request = request.replace(url='https://music.douban.com/subject/' + str(
                    spider.musiclist[spider.current_music]) + '/', )
                return self._retry(next_request, reason, spider) or response
            time.sleep(10)
            return self._retry(request, reason, spider) or response
        return response

    def process_exception(self, request, exception, spider):
        if isinstance(exception, self.EXCEPTIONS_TO_RETRY) \
                and not request.meta.get('dont_retry', False):
            time.sleep(10)
            return self._retry(request, exception, spider)
        elif isinstance(exception, TimeoutError):
            return request
