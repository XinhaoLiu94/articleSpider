# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
from articleSpider.items import ArticleItem
from articleSpider.utils.common import get_md5
import datetime



class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        #获取列表页的

        post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        for post_url in post_urls:
            yield Request(url = post_url,callback = self.parse_detail)

        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url = next_url,callback = self.parse)


    def parse_detail(self,response):
        article_item = ArticleItem()
        title = response.xpath('//*[@class="entry-header"]/h1/text()').extract()
        create_date = response.xpath('//*[@class="entry-meta"]/p/text()').extract()[0].strip().replace("·"," ").strip()
        praise_numbers = int(response.xpath('//*[@class=" btn-bluet-bigger href-style vote-post-up   register-user-only "]/h10/text()').extract()[0])
        favor_numbers = response.xpath('//*[@class=" btn-bluet-bigger href-style bookmark-btn  register-user-only "]/text()').extract()[0]
        match_re = re.match(".*(\d+).*",favor_numbers)
        if match_re:
            favor_numbers = int(match_re.group(1))
        else:
            favor_numbers = 0

        comment_numbers = response.xpath('//*[@class="btn-bluet-bigger href-style hide-on-480"]/text()').extract()[0]
        match_re = re.match(".*(d+).*",comment_numbers)
        if match_re:
            comment_numbers = int(match_re.group(1))
        else:
            comment_numbers = 0

        content = response.xpath("//div[@class='entry']").extract()[0]
        taglist = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()

        article_item["title"] = title
        article_item["url_object_id"] = get_md5(response.url)
        article_item["url"] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date,"%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        article_item["create_date"] = create_date
        article_item["praise_nums"] = praise_numbers
        article_item["comment_nums"] = comment_numbers
        article_item["favour_nums"] = favor_numbers
        article_item["tags"] = taglist
        article_item["content"] = content

        yield article_item
