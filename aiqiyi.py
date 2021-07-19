import requests
import json
import re

import pandas as pd


def get_iqy():
    #  电影起始数量
    pagenum = 0

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    # response=requests.get(url=url,headers=headers)
    # response.encoding="utf-8"
    # page_text=response.text
    # print(page_text)
    """
    """
    #
    temp_list = []  # 暂时存放单部电影的数据
    dataRes = []  # 每次循环把单部电影数据放到这个list
    hasNext = 1
    # for i in range(pagenum + 1, pagenum + 100):  # 循环100-1次

    while (hasNext != 0):
        # https://pcw-api.iqiyi.com/search/recommend/list?channel_id=1&data_type=1&market_release_date_level=2021&mode=24&page_id=4&ret_num=48&session=e76d98e79967fc20a6d7914efcfda2ee
        url_0 = "https://pcw-api.iqiyi.com/search/recommend/list?channel_id=1&data_type=1&mode=24&market_release_date_level=2021&page_id=" + str(
            pagenum) + "&ret_num=48&session=ad1d98bb953b7e5852ff097c088d66f2"
        pagenum = pagenum + 1
        # url_0 = url_0 + str(i) + "&ret_num=48&session=ad1d98bb953b7e5852ff097c088d66f2"
        print('url: ', url_0)  # 输出拼接好的url
        response = requests.get(url=url_0, headers=headers)
        response.encoding = "utf-8"
        page_text = response.text
        # 解析json对象
        json_obj = json.loads(page_text)
        hasNext = json_obj['data']['has_next']
        # hasNext = 0
        # print(hasNext)
        # 这里的异常捕获是因为     测试循环的次数有可能超过电影网站提供的电影数 为了防止后续爬到空的json对象报错
        try:
            json_list = json_obj['data']['list']
        except KeyError:
            return dataRes  # json为空 程序结束
        for j in json_list:  # 开始循环遍历json串
            # print(json_list)
            # 0 title
            name = j['name']  # 找到电影名 title
            # print(name)
            temp_list.append(name)
            # 1 period
            period = j['period']
            temp_list.append(period)
            # 异常捕获，防止出现电影没有description
            # 2 description
            try:
                score = j['description']  # description
                # print(score)
                temp_list.append(score)
            except KeyError:
                print("KeyError")
                temp_list.append("iqy暂无评分")  # 替换字符串

            link = j['categories']  # 找到categories
            temp_list.append(link)

            dataRes.append(temp_list)
            # print(temp_list)
            # temp_list = []

        # print('___________________________', len(json_list))

    return dataRes


if __name__ == '__main__':
    movieResult = get_iqy()
    # print(movieResult[0])
    title = []
    period = []
    description = []
    categories = []
    for j in movieResult:  # 开始循环遍历json串
        for idx, val in enumerate(j):
            if((idx+1)%4 == 1):
                title.append(val)
            if ((idx + 1) % 4 == 2):
                period.append(val)
            if ((idx + 1) % 4 == 3):
                description.append(val)
            if ((idx + 1) % 4 == 0):
                categories.append(''.join(val))



    # 任意的多组列表
    a = [1, 2, 3]
    b = [4, 5, 6]

    # 字典中的key值即为csv中列名
    dataframe = pd.DataFrame({'title': title, 'period': period, 'description': description, 'categories': categories})

    # 将DataFrame存储为csv,index表示是否显示行名，default=True
    dataframe.to_csv("/Users/Helen/Desktop/sample/script/test.csv", index=False, sep=',')
