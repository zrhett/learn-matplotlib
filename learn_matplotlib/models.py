import os
import pandas as pd
from sqlalchemy import create_engine
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side, PatternFill, Color
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta
from pandas_datareader import data


class DataModel:
    """数据模型基类"""
    stock_db_filename = 'stock.db'
    db_engine = create_engine('sqlite:///' + stock_db_filename)
    stocks = [
            {'name': 'Google', 'zone': 'US', 'code': 'GOOG'},
            {'name': 'Apple', 'zone': 'US', 'code': 'AAPL'},
            {'name': 'IBM', 'zone': 'US', 'code': 'IBM'},
            {'name': 'Alibaba', 'zone': 'US', 'code': 'BABA'},
            {'name': 'Amazon', 'zone': 'US', 'code': 'AMZN'},
            {'name': 'Tesla', 'zone': 'US', 'code': 'TSLA'}
        ]

    def __init__(self):
        self.__init_stocks()

    def __init_stocks(self):
        """构造数据库表名"""
        for stock in self.stocks:
            stock['sql_table'] = '_'.join([stock['zone'], stock['code']])

    def build_stocks_db(self):
        """重新获取所有数据"""
        for stock in self.stocks:
            print(f'获取：{stock["name"]}')
            df = data.DataReader(stock['code'], data_source='yahoo')
            df.to_sql(stock['sql_table'], self.db_engine, if_exists='replace')
        print('完成')

    def get_latest_stocks_data(self):
        """获取数据库中最后到今日的数据"""
        for stock in self.stocks:
            print(f'获取：{stock["name"]}')
            date_str = self.db_engine.execute(f'select max(Date) from {stock["sql_table"]}').fetchall()[0][0]
            start_date = datetime.strptime(date_str[:10], '%Y-%m-%d') + timedelta(days=1)

            if start_date.date() >= datetime.today().date():
                print(f'起始日期{start_date.date()}太近，跳过')
                continue
            else:
                print(f'起始日期{start_date.date()}')

            df = data.DataReader(stock['code'], data_source='yahoo', start=start_date)
            df = df[start_date:]
            num = len(df)
            if num > 0:
                df.to_sql(sql_table, self.db_engine, if_exists='append')
            print(f'存入{num}条数据')
        print('完成')

    def read_stock_from_db(self, table_name, start, end):
        """读取数据库表中指定时间范围内的数据"""
        sql = f'select * from {table_name} where Date>="{start}" and Date<"{end}"'
        return pd.read_sql(sql, self.db_engine, index_col='Date', parse_dates=['Date'])

    def read_all_stocks_to_dict(self, start, end):
        stock_list = list()

        for stock in self.stocks:
            stock_list.append(dict(name=stock['name'], data=self.read_stock_from_db(stock["sql_table"], start, end)))

        return stock_list
