from bokeh.core.property.pandas import pd

stockData = pd.read_csv('stock.csv', header=None)

print(stockData)
# for i in stockData:
#     print(stockData[i])