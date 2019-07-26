# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from ..items import SongInfoItem
from ..items import UpdateMusicInfoItem


class SonglistSpider(scrapy.Spider):
    name = 'SongList'
    allowed_domains = ['douban.com']
    myPipeline = None
    musiclist = None
    current_music = None

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
        yield scrapy.Request(url, callback=self.get_musics)

    def get_musics(self, response):
        account = response.xpath('//a[@class="bn-more"]/span/text()').extract_first()
        if account is None:
            print("登录失败")
        else:
            print(u"登录成功,当前账户为 %s" % account)

        musiclist = self.myPipeline.get_all_musics()
        self.musiclist = [i[0] for i in musiclist]
        self.current_music = 110285
        # TODO: 404 handler
        return [
            Request(
                url='https://music.douban.com/subject/' + str(
                    self.musiclist[
                        self.current_music]) + '/',
                # url='https://music.douban.com/subject/34433664/',
                callback=self.get_songs
            )
        ]

    def get_songs(self, response):
        music_info_raw = response.xpath('//div[@id="info"]//text()').getall()
        info_dict = {}
        music_info = []
        for info in music_info_raw:
            info_str = info.strip('\xa0\n\t ')
            if info_str:
                music_info.append(info_str)
        for info in music_info:
            if info == '流派:':
                info_dict['流派'] = music_info[int(music_info.index('流派:')) + 1]
            if info == '表演者:':
                info_dict['表演者'] = music_info[int(music_info.index('表演者:')) + 1]

        # print(info_dict)
        UMIT = UpdateMusicInfoItem()
        UMIT['itemid'] = self.musiclist[self.current_music]
        UMIT['style'] = None
        UMIT['player'] = None
        for key, value in info_dict.items():
            if key == '流派':
                UMIT['style'] = value
            if key == '表演者':
                UMIT['player'] = value
        yield UMIT

        song_list = response.xpath('//div[@class="track-list"]')

        if not song_list:
            song_list = response.xpath('//div[@class="song-items-wrapper"]')
            song_name_list = song_list.xpath('.//div[@class="col song-name-short"]/span/text()').getall()

        else:
            song_name_list = song_list.xpath('.//text()').getall()
            song_name_list = [song.strip('\xa0\n\t ') for song in song_name_list]
            song_name_list = list(filter(None, song_name_list))

        for song_name in song_name_list:
            SIT = SongInfoItem()
            SIT['songname'] = song_name
            SIT['itemid'] = self.musiclist[self.current_music]
            yield SIT

        # print(song_name_list)
        print(self.musiclist[self.current_music], self.current_music)

        self.current_music += 1
        yield Request(
            url='https://music.douban.com/subject/' + str(
                self.musiclist[
                    self.current_music]) + '/',
            callback=self.get_songs
        )
