# -*- coding: utf-8 -*-
import scrapy
from jsonpath import jsonpath
import json
from zhihu_crawl.items import *

class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['https://www.zhihu.com/api/v4/topics/19865724/followers?include=data%5B%2A%5D.gender%2Canswer_count%2Carticles_count%2Cfollower_count%2Cis_following%2Cis_followed&limit=20&offset=%d']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            # 'User-Agent':'Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html）',
            'Cookie': '_zap=4caef66b-64d0-4901-abcb-1b261f274783; __DAYU_PP=ivyNznrmezzMYeJIMZYv2ac38cbedc7c; d_c0="AFAjt1u9mw2PTmg-a5lNCpyuGubLfSD1JuA=|1526569812"; q_c1=f4ba2ee031d248188d6e99bb1e12b27d|1526569974000|1514737539000; l_cap_id="MzM4YTFmZjU2MWViNDFhMTgyOTY0M2JlNDBhM2FkZDQ=|1526805631|f5e3abbd52eb072acbf018730f1f9d285ed6cf3d"; r_cap_id="NmU4ZTUzYjhkZTY1NDAxOGFlZDdhYjYwZmI1YTY4ZGI=|1526805631|9ac6d1313d3bccf985f84549fb1a78bb35c60c90"; cap_id="ZjcwNzhjYTExNjJmNGNmOWEyYzU5OGFkMzRmODE5Y2Y=|1526805631|02ad17ac8f6e757ead7a460f93dd58fda016701a"; tgw_l7_route=4902c7c12bebebe28366186aba4ffcde; _xsrf=8de1e440-0caa-48f0-aee8-bc83cfe3c9e4; z_c0="2|1:0|10:1527069913|4:z_c0|92:Mi4xMkVVbUF3QUFBQUFBVUNPM1c3MmJEU1lBQUFCZ0FsVk4yWXJ5V3dCWlpqeFRVSTRfSUpBekh0OXl0anV1VmNvemZR|b51af657f89509ead31d7d74e5492e9cdf4bb10858e9b19d6c0569094b4138b9"; capsion_ticket="2|1:0|10:1527069937|14:capsion_ticket|44:MTA3MmQwZDZlOGNlNGYxOWJjNjdmOWFkZGJlMzEzYTE=|f8dd7841f8ee15a1a132a2bdda8c6ca54cb961d429237cf359a72d6f655e2101"; __utma=155987696.908685652.1515245491.1515245491.1527069962.2; __utmb=155987696.0.10.1527069962; __utmc=155987696; __utmz=155987696.1527069962.2.2.utmcsr=baidu|utmccn=(organic)|utmcmd=organic',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36'
        },
        'COOKIES_ENABLED': False,
        'LOG_LEVEL ': 'DEBUG',
    }
    # 'https://www.zhihu.com/api/v4/members/suchangmao/followers?include=data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics&offset=20&limit=20'
    follows_api = 'https://www.zhihu.com/api/v4/members/{}/followers?include={}&limit=20&offset={}'
    follows_query = 'data%5B*%5D.answer_count%2Carticles_count%2Cgender%2Cfollower_count%2Cis_followed%2Cis_following%2Cbadge%5B%3F(type%3Dbest_answerer)%5D.topics'
    people_api = 'https://www.zhihu.com/api/v4/members/{}/activities'
    tokens_list = ['suchangmao']
    tokens_pop = None
    def start_requests(self):
        self.tokens_pop = self.tokens_list.pop()
        #对起始token进行爬取
        yield scrapy.Request(self.follows_api.format(self.tokens_pop,self.follows_query,0),self.parse)
        yield scrapy.Request(self.people_api.format(self.tokens_pop),self.user_api)
    def parse(self, response):
        tokens = jsonpath(json.loads(response.text),'$..url_token')
        isend = jsonpath(json.loads(response.text),'$..is_end')[0]
        next = jsonpath(json.loads(response.text),'$..next')
        #如果能够获取,加入列表
        if tokens:
            self.tokens_list.extend(tokens)
        # print(tokens)
        #判断单个任务是否结束,返回True说明结束
        if isend:
            #重新弹出一个用户token进行抓取
            self.tokens_pop = self.tokens_list.pop()
            yield scrapy.Request(self.follows_api.format(self.tokens_pop, self.follows_query, 0),self.parse)
            yield scrapy.Request(self.people_api.format(self.tokens_pop), self.user_api)
            return
        if next:
            next_url = next[0]
            yield scrapy.Request(next_url, self.parse)

    def user_api(self,response):
        api_url = jsonpath(json.loads(response.text),'$..data[0].actor.url')[0]
        print(api_url)
        yield scrapy.Request(api_url,self.detail_parse,dont_filter=True)
    def detail_parse(self,response):
        item = ZhihuCrawlItem()
        data = json.loads(response.text)
        info_name = jsonpath(data,'$..name')
        name,company,university,location,industry,*surplus = info_name
        item['name'] = name
        item['company'] = company
        item['university'] = university
        item['location'] = location
        item['industry'] = industry
        yield item