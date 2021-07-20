import requests
import bs4
from collections import OrderedDict
from pandas import DataFrame
import pandas as pd


# Prevent Pandas from folding long urls
pd.set_option('display.max_colwidth', -1)

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.113 Safari/537.36'
}

# base_url = 'https://v.qq.com/x/bu/pagesheet/list?append=1&channel=movie&itype=100061&listpage=2&offset={offset}&pagesize={page_size}'

# 豆瓣最佳
DOUBAN_BEST_SORT = 21

NUM_PAGE_DOUBAN = 100  #167

def get_soup(year,page_idx, page_size=30, sort=DOUBAN_BEST_SORT):
    base_url = 'https://v.qq.com/x/bu/pagesheet/list?_all=1&append=0&channel=movie&listpage=1&offset={offset}&pagesize={page_size}&sort=18&year={year}'
    url = base_url.format(offset=page_idx * page_size, page_size=page_size,
                        year=year)
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.content.decode('utf-8'), 'lxml')
    return soup

def find_list_items(soup):
    return soup.find_all('div', class_='list_item')

def douban_films(year):
    rel = []
    for p in range(NUM_PAGE_DOUBAN):
        print('Getting page {}'.format(p))
        soup = get_soup(year,p)
        # print(soup)
        rel += find_list_items(soup)
    return rel

def parse_films(films):
    '''films is a list of `bs4.element.Tag` objects'''
    rel = []
    for i, film in enumerate(films):
        # print(film)
        title = film.find('a', class_="figure_title")['title']
        print('Parsing film %d: ' % i, title)
        link = film.find('a', class_="figure")['href']
        # remove "preceding \\" to find the accessible URL
        img_link = film.find('img', class_="figure_pic")['src']

        # test if need VIP
        need_vip = bool(film.find('img', class_="mark_v"))
        score = getattr(film.find('div', class_='figure_score'), 'text', None)
        if score: score = float(score)
        cast = film.find('div', class_="figure_desc")
        if cast:
            cast = cast.get('title', None)
        play_amt = film.find('div', class_="figure_count").get_text()

        # db_score, db_link =search_douban(title)
        # Store key orders
        dict_item = OrderedDict([
            ('title', title),
            ('vqq_score', score),
            # ('douban_score', db_score),
            ('need_vip', need_vip),
            ('cast', cast),
            ('play_amount', play_amt),
            # ('vqq_play_link', link),
            # ('db_discuss_link', db_link),
            # ('img_link', img_link),
        ])

        rel.append(dict_item)

    return rel


def search_douban(film_name):

    url = 'https://www.douban.com/search?q={film_name}'.format(film_name=film_name)
    res = requests.get(url,headers=headers)  # 要加上headers 才可以操作
    soup = bs4.BeautifulSoup(res.content, 'lxml')
    print('soup empty: ',soup)
    score = getattr(soup.find('div', class_="result").find('span', class_="rating_nums"), 'text', None)
    # content = getattr(soup.find('div', class_="result").find('p'), 'text', '没找到')
    # print(content)
    if score: score = float(score)
    douban_link = soup.find('div', class_="result").find('a').get('href', None)
    return score, douban_link

if __name__ == '__main__':
    yearList = [2021, 2020, 2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009]

    for year in yearList:
        df = DataFrame(parse_films(douban_films(year)))
        # Sorted by score
        df.sort_values(by="vqq_score", inplace=True, ascending=False)
        # Format links
        # df['vqq_play_link'] = df['vqq_play_link'].apply(lambda x: '<a href="{0}">Film link</a>'.format(x))
        # df['img_link'] = df['img_link'].apply(lambda x: '<img src="{0}">'.format(x))

        # Chinese characters in Excel must be encoded with _sig
        df.to_csv('vqq_films_{year}.csv'.format(year = year), index=False, encoding='utf_8_sig')
        # Pickle
        # df.to_pickle('vqq_douban_films.pkl')
        # # HTML, render hyperlink
        # df.to_html('vqq_douban_films.html', escape=False)