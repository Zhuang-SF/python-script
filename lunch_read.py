#!/usr/bin/env python
# encoding: utf-8

"""
__author__: Widsom Zhang
__time__: 2017/11/14 12:48
"""

import urllib.request
import urllib.parse
from lxml import etree
from lxml.html import fromstring
from IPython.display import display, HTML

import sqlite3
from sqlite3 import Error


class JanDanSpider(object):
    def __init__(self):
        """
        初始化数据，如headers,xpath的解析规则
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
        }
        self.rule_large = "//ol[@class='commentlist']/li//a[@class='view_img_link']/@href"
        self.rule_normal = "//ol[@class='commentlist']/li//img/@src"
        self.rule_pre_page = "//div[@class='comments']//a[@class='previous-comment-page']/@href"
        self.rule_table = "//table/tbody/tr/td"
        self.rule_table_date = "//tbody/tr/td[@class='xl75']/span/span"

        self.host = "intranet.phoenixtv.com"

    def set_rule_large(self, rule_large):
        """
        对大图规则进行修改
        :param rule_large: 大图获取的规则
        :return:
        """
        self.rule_large = rule_large

    def set_rule_normal(self, rule_normal):
        """
        对正常图规则进行修改
        :param rule_normal: 正常图获取的规则
        :return:
        """
        self.rule_normal = rule_normal

    def set_rule_pre_page(self, rule_pre_page):
        """
        对获取上一页的规则进行修改
        :param rule_pre_page:   上一页的规则
        :return:
        """
        self.rule_pre_page = rule_pre_page

    def set_host(self, host):
        """
        对host进行赋值
        :param host:
        :return:
        """
        self.host = host

    def load_page(self, url):
        """
        通过url加载网页数据
        :param url: 请求的url
        :return:
        """
        # 输出url
        print(url)
        # 加强判断
        if self.host in url:
            print(self.host)
            # 获取服务端的响应数据
            text = self.get_response(url)
            print("\xe9\xa3\x9f\xe5\xa0\x82".encode('raw_unicode_escape').decode())
            # 解析我们的 table
            # print(self.rule_table)
            # print(self.parse_page_html(text, self.rule_table))

            #  直接在这里搞

            entry = etree.HTML(text).xpath('//table/tbody/tr/td/div/img')
            print(entry[0].get('src'))
            print(entry[1].get('src'))

            anotherEntry = etree.HTML(text).xpath('//table/tbody/tr/td/table/tbody/tr')

            # anotherEntry[0][1][0][0].text
            obj = []
            i = 0
            j = 0

            class RowWW(object):
                def __init__(self, number):
                    self.content = number

            # 20 行
            # print(len(anotherEntry))
            #       每一行的 列数
            # print(len(anotherEntry[0]))
            # anotherEntry[0] 首先我们的 anotherEntry 会获取我们的 tr 下面所有的 td
            # anotherEntry[0] 就是我们的第一个 td 也就是第一行的所有内容
            # len(anotherEntry[0]) 就是第一行 td 有多少个列

            while j < len(anotherEntry):
                bigRow = RowWW([])
                for column in anotherEntry[j]:
                    try:
                        bb = column[0][0].text
                    except:
                        bb = column[0].text
                    if (bb == None):
                        bb = ''
                    else:
                        bb = bb.replace(u'\xa0', u' ')
                    bigRow.content.append(bb)
                obj.append(bigRow)
                j = j + 1

            for menu in obj:
                print(menu.content)
            #

            #     Next 就是把这部分的数据写入数据库了

            return
            database = r"/Users/Helen/Library/Mobile Documents/com~apple~CloudDocs/Wang/Develop/db/text.sqlite"

            # create a database connection
            conn = self.create_connection(database)
            with conn:
                # create a new project
                project = ('Cool App with SQLite & Python', '2015-01-01', '2015-01-30');
                project_id = self.create_project(conn, project)

                # tasks
                task_1 = ('Analyze the requirements of the app', 1, 1, project_id, '2015-01-01', '2015-01-02')
                task_2 = ('Confirm with user about the top requirements', 1, 1, project_id, '2015-01-03', '2015-01-05')

                # create tasks
                self.create_task(conn, task_1)
                self.create_task(conn, task_2)

            # # print(type(anotherEntry))
            # # print(anotherEntry[8])
            # # print(anotherEntry[8].encode('raw_unicode_escape').decode())
            # cleanList = list(map(lambda x: x.replace(u'\xa0', u' '),anotherEntry))
            # print(cleanList)
            # print(len(cleanList))

            # items = ['1', '2', '3','4', None]
            # squared = list(map(lambda x: x ** 2, items))

            # print(squared)

            # print(items[4].encode('raw_unicode_escape').decode())

            # self.load_tables(self.parse_page_html(text, self.rule_table))
            # 通过大图的解析规则，下载大图
            # self.deal_images(self.parse_page(text, self.rule_large))
            # 通过正常图的解析规则，下载正常图
            # self.deal_images(self.parse_page(text, self.rule_normal))
            # 通过下一页的解析规则，加载下一页
            # self.deal_pre_page(self.parse_page(text, self.rule_pre_page))

    def create_connection(self,db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        try:
            conn = sqlite3.connect(db_file)
        except Error as e:
            print('看看 呃呃呃',e)

        return conn

    def create_project(self,conn, project):
        """
        Create a new project into the projects table
        :param conn:
        :param project:
        :return: project id
        """
        sql = ''' INSERT INTO projects(name,begin_date,end_date)
                  VALUES(?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, project)
        conn.commit()
        return cur.lastrowid

    def create_task(self,conn, task):
        """
        Create a new task
        :param conn:
        :param task:
        :return:
        """

        sql = ''' INSERT INTO tasks(name,priority,status_id,project_id,begin_date,end_date)
                  VALUES(?,?,?,?,?,?) '''
        cur = conn.cursor()
        cur.execute(sql, task)
        conn.commit()
        return cur.lastrowid

    def get_response(self, url):
        """
        通请求的url，获取服务端返回的数据
        :param url: 请求url
        :return: 服务端返回的数据
        """
        req = urllib.request.Request(url, headers=self.headers)
        return urllib.request.urlopen(req).read()

    def parse_page_html(self, text, rule):
        # 获取了一整个 html 对象
        html = etree.HTML(text)
        # print(html.xpath(rule))
        return html.xpath(rule)

    def load_tables(self, elements):

        if elements is not None:
            print('type::: ', type(elements), elements)
            # for img in elements.xpath("//img"):
            #     print(img[0].get('src'))

            # /table/tbody/tr/td["@class='xl66']
            # atable = tables[15].xpath("//table/tbody/tr")
            # print('输出： ',atable[0])
            # for a in atable[0]:
            #     print('a')
            #     self.load_table(a.xpath("//span/span"))

    def load_table(self, item):
        for a in item:
            print('haohao ', a.text)

    def parse_page(self, text, rule):
        """
        解析页面
        :param text: 服务端返回的数据
        :param rule: 解析规则
        :return: 返回解析页面的结果
        """
        # 通过etree库，将服务端返回的页面数据封装成html对象
        html = etree.HTML(text)
        # 通过xpath规则解析html对象，返回数据列表
        return html.xpath(rule)

    def deal_images(self, images):
        """
        处理页面解析获得的图片
        :param images: 解析页面返回的图片集合
        :return:
        """
        if images is not None:
            # 遍历数据列表
            for image in images:
                if 'http:' not in image:
                    # 拼接图片的url
                    image = 'http:' + image
                print(image)
                # 下载图片
                self.load_image(image)
                # self.write_image_url(image)

    def deal_pre_page(self, results):
        """
        处理下一页
        :param results: 解析页面结果
        :return:
        """
        if results is not None:
            # 因为在页面有2处，解析有2个一样的地址
            if len(results) > 0:
                # 取第一个
                url = results[0]
                print(url)
                if self.host in url:
                    if 'http:' not in url:
                        # 拼接字符串
                        url = 'http:' + url
                        # 加载下一个页面
                        self.load_page(url)

    def load_image(self, image_url):
        """
        下载图片
        :param image_url: 图片的url
        :return:
        """
        with open(self.create_filename(image_url), 'wb')as f:
            f.write(self.get_response(image_url))

    def write_image_url(self, image_url):
        """
        将图片的url写入到文件
        :param image_url: 图片的url
        :return:
        """
        with open('imageurl.txt', 'a')as f:
            f.write(image_url + "\n")

    def create_filename(self, image_url):
        """
        通过图片的url来确定存储路径
        :param image_url:   图片的url
        :return:
        """
        results = image_url.split('/')
        if 'large' in image_url:
            filename = 'image/large/' + results[-1]
        else:
            filename = 'image/normal/' + results[-1]
        return filename


if __name__ == '__main__':
    """
        爬取网站示例：http://jandan.net/ooxx

        需求：爬取页面的图片

        爬取网站思路：

            1. 该网站页面，本身包含了大量图片，有查看大图，有直接显示的jpg/gif等图片。可以通过浏览器的检查工具，分析具体的图片url的位置。
            2. 网站有直接显示的是最新的内容，过去的内容在可以通过上一页的按钮找到
            3. 网站上一页和下一页的url比较有规律：如：http://jandan.net/ooxx/page-287#comments，可以通过page-count的形式匹配
                    ，不过我们直接通过网页的previous-comment-page的class来获取上一页的url。
            4. 通过浏览器的xpath-helper工具，输入匹配规则，找到我们需要的内容。


        代码构思：

            爬取网站主要分为这样几个步骤：

                1. 请求url，获取响应数据
                2. 通过xpath的解析规则解析页面
                3. 解析页面后进行对应逻辑处理
                4. 加载图片，写入文件
                5. 解析到上一页的url，再次进行请求，随后一直递归

    """

    # 爬取的网站
    url = "http://intranet.phoenixtv.com/dept_page.shtml?dept=15&navid=18"
    spider = JanDanSpider()
    spider.load_page(url)
