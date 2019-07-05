from learn_matplotlib.models import DataModel

model = DataModel()
# model.build_stocks_db()
# model.get_latest_stocks_data()
# print(model.get_latest_date_from_db('US_AAPL'))
print(model.read_stock_from_db('US_IBM', '2018-01-01', '2019-01-01'))