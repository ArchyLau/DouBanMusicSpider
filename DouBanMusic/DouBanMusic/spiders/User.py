# -*- coding: utf-8 -*-
import scrapy
from scrapy.http.cookies import CookieJar
from scrapy.selector import Selector
from ..items import DoubanUserItem
import re


class UserSpider(scrapy.Spider):
    name = 'User'
    default_headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': 1,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    }
    allowed_domains = ['www.douban.com']
    start_index = 0

    def start_requests(self):
        start_url = 'https://www.douban.com/group/nomusiciwilldie/members?start=130620'
        yield scrapy.Request(url=start_url, headers=self.default_headers, callback=self.get_members)

    # Done
    def get_managers(self, response):
        managers_href_tmp = response.xpath(
            '//div[@class="obss name indent"]/dl/dd/a/@href').getall()
        managers_name_tmp = response.xpath(
            '//div[@class="obss name indent"]/dl/dd/a/text()').getall()
        managers_imgurl_tmp = response.xpath(
            '//div[@class="obss name indent"]/dl/dt/a/img[@class="m_sub_img"]/@src').getall()
        # print(managers_doubanid_tmp)
        for (href, name, imgurl) in zip(managers_href_tmp, managers_name_tmp, managers_imgurl_tmp):
            UserItem = DoubanUserItem()
            doubanid = re.search('u\d.*-', imgurl)
            if doubanid is not None:
                UserItem['href'] = href
                UserItem['name'] = name
                UserItem['doubanid'] = int(doubanid.group().strip('u-'))
            else:
                UserItem['href'] = None
                UserItem['name'] = None
                UserItem['doubanid'] = None
            # print(UserItem)
            yield UserItem

        next_page = response.xpath('//link[@rel="next"]/@href').get()
        members_url = 'https://www.douban.com/group/nomusiciwilldie/members?start=0'
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, headers=self.default_headers, callback=self.get_managers)
        else:
            yield scrapy.Request(members_url, headers=self.default_headers, callback=self.get_members)
            # return

    def get_members(self, response):
        members_href_tmp = response.xpath(
            '//div[@class="member-list"]//div[@class="name"]/a/@href').getall()
        members_name_tmp = response.xpath(
            '//div[@class="member-list"]//div[@class="name"]/a/text()').getall()
        members_imgurl_tmp = response.xpath(
            '//div[@class="member-list"]//div[@class="pic"]/a/img[@class="imgnoga"]/@src').getall()
        for (href, name, imgurl) in zip(members_href_tmp, members_name_tmp, members_imgurl_tmp):
            UserItem = DoubanUserItem()
            doubanid = re.search('u\d.*-', imgurl)
            if doubanid is not None:
                UserItem['href'] = href
                UserItem['name'] = name
                UserItem['doubanid'] = int(doubanid.group().strip('u-'))
            else:
                UserItem['href'] = None
                UserItem['name'] = None
                UserItem['doubanid'] = None
            # print(UserItem)
            yield UserItem
        next_page = response.xpath('//link[@rel="next"]/@href').get()
        if next_page is not None:
            next_page = response.urljoin(next_page)
            yield scrapy.Request(next_page, headers=self.default_headers, callback=self.get_members)
        else:
            return
