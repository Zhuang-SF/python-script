from bokeh.core.property.pandas import pd

stockData = pd.read_csv('stock.csv', header=None,names=['类型','股票代号','股票名称','购买价格','数量','状态','成交数量','日期','交易类型','交易状态','是否竞价'])

print(stockData)
# for i in stockData:
#     print(stockData[i])