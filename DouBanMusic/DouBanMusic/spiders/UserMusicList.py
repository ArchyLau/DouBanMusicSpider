# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest, Request


class UsermusiclistSpider(scrapy.Spider):
    # 先check一遍三列表全空的用户
    # 查看广播和个人主页需要模拟登陆，其他不需要
    name = 'UserMusicList'
    allowed_domains = ['douban.com']
    myPipeline = None
    userlist = None
    collect_none_users = []
    wish_none_users = []
    do_none_users = []
    current_user = None

    # start_urls = ['http://douban/']
    def start_requests(self):
        # 只是为了启动spider 以从pipeline中获取Users, url可随意设置
        return [Request(
            url='https://accounts.douban.com/passport/login',
            callback=self.get_users
        )]

    def get_users(self, response):
        userlist = self.myPipeline.get_all_users()
        self.userlist = [i[0] for i in userlist]
        self.current_user = 0
        return [
            Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[
                        self.current_user]) + '/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_collect
            )
        ]

    def music_collect(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        ).getall()
        if not item_list:
            self.collect_none_users.append(self.current_user)
        return [
            Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[self.current_user]) + '/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_wish
            )
        ]

    def music_wish(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        ).getall()
        if not item_list:
            self.wish_none_users.append(self.current_user)
        return [
            Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[self.current_user]) + '/do?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_do
            )
        ]

    def music_do(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        ).getall()
        if not item_list:
            self.wish_none_users.append(self.current_user)
        if 100 - self.current_user > 1:
            self.current_user += 1
            return [
                Request(
                    url='https://music.douban.com/people/' + str(
                        self.userlist[
                            self.current_user]) + '/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                    # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                    callback=self.music_collect
                )
            ]
        else:
            # 求三个list的交集，即全空用户，再用userlist
            all_none_users = list((set(self.collect_none_users).intersection(set(self.wish_none_users))).intersection(
                set(self.do_none_users)))
            f = open('./all_none_users.txt', 'a', encoding='utf8')
            f.write(str(all_none_users))
            f.close()
            print(len(all_none_users))
