# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import FormRequest, Request
from ..items import UserMusicCollectItem
from ..items import UserMusicWishItem
from ..items import UserMusicDoItem
from ..items import MusicInfoItem


class UsermusiclistSpider(scrapy.Spider):
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
        # 加入登录操作，提高反爬
        login_data = {
            'ck': '',
            'name': '18717882007',
            'password': 'lyq963852',
            'remember': 'True',
            'ticket': ''
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
        headers['X-Requested-With'] = 'XMLHttpRequest'
        return [scrapy.FormRequest(
            # url='https://accounts.douban.com/passport/login',
            url='https://accounts.douban.com/j/mobile/login/basic',
            formdata=login_data,
            headers=headers,
            callback=self.login
        )]

    def login(self, response):
        url = 'http://www.douban.com/'
        yield scrapy.Request(url, callback=self.get_users)

    def get_users(self, response):
        # print(response.text)
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            print("登录失败")
        else:
            print(u"登录成功,当前账户为 %s" % account)
        userlist = self.myPipeline.get_all_users()
        self.userlist = [i[0] for i in userlist]
        self.current_user = 7062
        return [
            Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[
                        self.current_user]) + '/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/Rocwong/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_collect
            )
        ]

    def music_collect(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        )
        if not item_list:
            self.collect_none_users.append(self.current_user)
        else:
            for item in item_list:
                raw_id = item.xpath('./@id').get()
                item_show = item.xpath('./div[@class="item-show"]')
                raw_name = item_show.xpath('./div[@class="title"]/a/text()').get()
                # rating 空时为None 有rating时 需要跳过rating span获取date
                raw_rating = item_show.xpath('./div[@class="date"]/span/@class').get()
                raw_date = item_show.xpath('./div[@class="date"]/text()').extract()

                if raw_rating == None:
                    date = raw_date[0].strip('\xa0\n ')
                    rating = None
                else:
                    date = raw_date[1].strip('\xa0\n ')
                    rating = raw_rating.strip('rating-')

                item_hide = item.xpath('./div[@class="hide"]')
                content = item_hide.xpath('./div/span/text()').get()
                # 处理Item (UserMusicCollectItem、MusicInfoItem)
                id = raw_id.strip('list\n ')
                name = raw_name.strip('\xa0\n ')

                UMCI = UserMusicCollectItem()
                MI = MusicInfoItem()
                MI['itemid'] = id
                MI['name'] = name
                MI['content'] = content
                yield MI
                UMCI['userid'] = self.userlist[self.current_user]
                UMCI['itemid'] = id
                UMCI['rating'] = rating  # 可能是None
                UMCI['date'] = date
                yield UMCI
        # 加一个翻页机制
        next_page = response.xpath(
            '//link[@rel="next"]/@href'
        ).get()
        if next_page is not None:
            yield Request(
                url=next_page,
                callback=self.music_collect
            )
        else:
            yield Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[self.current_user]) + '/wish?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_wish
            )

    def music_wish(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        )
        if not item_list:
            self.wish_none_users.append(self.current_user)
        else:
            for item in item_list:
                raw_id = item.xpath('./@id').get()
                item_show = item.xpath('./div[@class="item-show"]')
                raw_name = item_show.xpath('./div[@class="title"]/a/text()').get()
                # rating 空时为None 有rating时 需要跳过rating span获取date
                raw_rating = item_show.xpath('./div[@class="date"]/span/@class').get()
                raw_date = item_show.xpath('./div[@class="date"]/text()').extract()

                if raw_rating == None:
                    date = raw_date[0].strip('\xa0\n ')
                    rating = None
                else:
                    date = raw_date[1].strip('\xa0\n ')
                    rating = raw_rating.strip('rating-')

                item_hide = item.xpath('./div[@class="hide"]')
                content = item_hide.xpath('./div/span/text()').get()
                # 处理Item (UserMusicCollectItem、MusicInfoItem)
                id = raw_id.strip('list\n ')
                name = raw_name.strip('\xa0\n ')

                UMWI = UserMusicWishItem()
                MI = MusicInfoItem()
                MI['itemid'] = id
                MI['name'] = name
                MI['content'] = content
                yield MI
                UMWI['userid'] = self.userlist[self.current_user]
                UMWI['itemid'] = id
                UMWI['rating'] = rating  # 可能是None
                UMWI['date'] = date
                yield UMWI
        next_page = response.xpath(
            '//link[@rel="next"]/@href'
        ).get()
        if next_page is not None:
            yield Request(
                url=next_page,
                callback=self.music_wish
            )
        yield Request(
            url='https://music.douban.com/people/' + str(
                self.userlist[self.current_user]) + '/do?sort=time&start=0&filter=all&mode=list&tags_sort=count',
            # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
            callback=self.music_do
        )

    def music_do(self, response):
        item_list = response.xpath(
            '//ul[@class="list-view"]/li[@class="item"]'
        )
        if not item_list:
            self.wish_none_users.append(self.current_user)
        else:
            for item in item_list:
                raw_id = item.xpath('./@id').get()
                item_show = item.xpath('./div[@class="item-show"]')
                raw_name = item_show.xpath('./div[@class="title"]/a/text()').get()
                # rating 空时为None 有rating时 需要跳过rating span获取date
                raw_rating = item_show.xpath('./div[@class="date"]/span/@class').get()
                raw_date = item_show.xpath('./div[@class="date"]/text()').extract()

                if raw_rating == None:
                    date = raw_date[0].strip('\xa0\n ')
                    rating = None
                else:
                    date = raw_date[1].strip('\xa0\n ')
                    rating = raw_rating.strip('rating-')

                item_hide = item.xpath('./div[@class="hide"]')
                content = item_hide.xpath('./div/span/text()').get()
                # 处理Item (UserMusicCollectItem、MusicInfoItem)
                id = raw_id.strip('list\n ')
                name = raw_name.strip('\xa0\n ')

                UMDI = UserMusicDoItem()
                MI = MusicInfoItem()
                MI['itemid'] = id
                MI['name'] = name
                MI['content'] = content
                yield MI
                UMDI['userid'] = self.userlist[self.current_user]
                UMDI['itemid'] = id
                UMDI['rating'] = rating  # 可能是None
                UMDI['date'] = date
                yield UMDI
        next_page = response.xpath(
            '//link[@rel="next"]/@href'
        ).get()
        if next_page is not None:
            yield Request(
                url=next_page,
                callback=self.music_do
            )

        if 10000 - self.current_user > 1:
            self.current_user += 1
            yield Request(
                url='https://music.douban.com/people/' + str(
                    self.userlist[
                        self.current_user]) + '/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                # url='https://music.douban.com/people/188676330/collect?sort=time&start=0&filter=all&mode=list&tags_sort=count',
                callback=self.music_collect
            )
        else:
            # 求三个list的交集，即全空用户，再用userlist
            all_none_users = list((set(self.collect_none_users).intersection(set(self.wish_none_users))).intersection(
                set(self.do_none_users)))
            f = open('./all_none_users.txt', 'a', encoding='utf8')
            f.write(str(all_none_users) + '\n')
            f.write(str(self.collect_none_users) + '\n')
            f.write(str(self.wish_none_users) + '\n')
            f.write(str(self.do_none_users) + '\n')
            f.close()
            print(len(all_none_users))
