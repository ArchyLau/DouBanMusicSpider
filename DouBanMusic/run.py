from scrapy import cmdline
# cmd_str='scrapy crawl User'
# cmd_str='scrapy crawl Proxy'
# cmd_str='scrapy crawl Padaili'
cmd_str='scrapy crawl UserMusicList'
cmdline.execute(cmd_str.split(' '))