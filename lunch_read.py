"""
__author__: Widsom Zhang
__New_author__ Wang Zhou
__time__: 2017/11/14 12:48
"""

import urllib.request
import urllib.parse
from lxml import etree

import sqlite3
from sqlite3 import Error


def create_lunch(conn, lunchObj):
    # print(lunchObj.date, lunchObj.weekOfDay, lunchObj.menuA, lunchObj.menuB, lunchObj.menuC, lunchObj.all)
    sql = ''' INSERT INTO lunch(menuDate,weekOfDay,menuA,menuB,menuC,menuAll)
                      VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql,
                (lunchObj.date, lunchObj.weekOfDay, lunchObj.menuA, lunchObj.menuB, lunchObj.menuC, lunchObj.all))
    conn.commit()
    return cur.lastrowid


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print('error when connection db', e)

    return conn


class JanDanSpider(object):
    def __init__(self):
        """
        初始化数据，如headers,xpath的解析规则
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
        }
        self.rule_table = "//table/tbody/tr/td"
        self.rule_table_date = "//tbody/tr/td[@class='xl75']/span/span"

        self.host = "intranet.phoenixtv.com"

    def get_response(self, url):
        """
        通请求的url，获取服务端返回的数据
        :param url: 请求url
        :return: 服务端返回的数据
        """
        req = urllib.request.Request(url, headers=self.headers)
        return urllib.request.urlopen(req).read()

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
            print(len(anotherEntry))

            while j < len(anotherEntry):
                bigRow = RowWW([])
                for column in anotherEntry[j]:
                    # print('column : aaa ',column, column.text)
                    # NOte： 以前用一层层的到里面去获取才能拿到，
                    #  现在发现直接 .text 就能获取了
                    # try:
                    #     bb = column[0][0].text
                    # except:
                    #     try:
                    #         bb = column[0].text
                    #     except:
                    #         bb = column.text
                    # print('搞毛啊', bb)
                    bb = column.text
                    if (bb == None):
                        bb = ''
                    else:
                        bb = bb.replace(u'\xa0', u' ')
                    bigRow.content.append(bb)
                obj.append(bigRow)
                j = j + 1





            class DailyMenu(object):
                def __init__(self, date, weekOfDay, menuA, menuB, menuC, all):
                    self.date = date
                    self.weekOfDay = weekOfDay
                    self.menuA = menuA
                    self.menuB = menuB
                    self.menuC = menuC
                    self.all = all

            dailyMenuArray = []
            indexOfMenu = 1
            while indexOfMenu < 6:
                date = obj[0].content[indexOfMenu]
                weekOfDay = obj[1].content[indexOfMenu]
                menuA = obj[3].content[indexOfMenu] + ',' + obj[4].content[indexOfMenu] + ',' + obj[5].content[
                    indexOfMenu]
                menuB = obj[8].content[indexOfMenu] + ',' + obj[9].content[indexOfMenu] + ',' + obj[10].content[
                    indexOfMenu]
                menuC = obj[13].content[indexOfMenu] + ',' + obj[14].content[indexOfMenu] + ',' + obj[15].content[
                    indexOfMenu]
                all = obj[18].content[indexOfMenu] + ',' + obj[19].content[indexOfMenu] + ',' + obj[20].content[
                    indexOfMenu]
                indexOfMenu = indexOfMenu + 1
                dailyMenuArray.append(DailyMenu(date, weekOfDay, menuA, menuB, menuC, all))

            print(dailyMenuArray[2])
            i = 0

            #     Next 就是把这部分的数据写入数据库了

            database = r"/Users/Helen/Library/Mobile Documents/com~apple~CloudDocs/Wang/Develop/db/text.sqlite"

            # create a database connection
            conn = create_connection(database)

            with conn:
                while i < 5:
                    create_lunch(conn, dailyMenuArray[i])
                    i = i + 1


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
