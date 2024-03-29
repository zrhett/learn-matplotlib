import os
import pandas as pd
from sqlalchemy import create_engine
from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, Side, PatternFill, Color
from openpyxl.utils.dataframe import dataframe_to_rows
from datetime import datetime, timedelta
from pandas_datareader import data
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

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
            {'name': 'Tesla', 'zone': 'US', 'code': 'TSLA'},
            {'name': 'Baidu', 'zone': 'US', 'code': 'BIDU'},
            {'name': 'Sina', 'zone': 'US', 'code': 'SINA'}
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
            if len(df) > 0:
                df.to_sql(stock['sql_table'], self.db_engine, if_exists='replace')
        print('完成')

    def is_table_exist(self, table_name):
        """数据库中是否存在指定表"""
        return self.db_engine.execute(f'select count(*) from sqlite_master where type="table" and name="{table_name}"').fetchall()[0][0] > 0

    def get_latest_stocks_data(self):
        """获取数据库中最后到今日的数据"""
        for stock in self.stocks:
            print(f'获取：{stock["name"]}')
            if self.is_table_exist(stock['sql_table']):
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
                    df.to_sql(stock['sql_table'], self.db_engine, if_exists='append')
            else:
                df = data.DataReader(stock['code'], data_source='yahoo')
                num = len(df)
                if num > 0:
                    df.to_sql(stock['sql_table'], self.db_engine, if_exists='replace')
            print(f'存入{num}条数据')
        print('完成')

    def read_stock_from_db(self, table_name, start, end):
        """读取数据库表中指定时间范围内的数据"""
        sql = f'select * from {table_name} where Date>="{start}" and Date<"{end}"'
        return pd.read_sql(sql, self.db_engine, index_col='Date', parse_dates='Date')

    def read_all_stocks_to_dict(self, start, end):
        stock_list = list()

        for stock in self.stocks:
            stock_list.append(dict(name=stock['name'], data=self.read_stock_from_db(stock['sql_table'], start, end)))

        return stock_list

    def read_all_stocks_close_from_db(self, start, end):
        """读取数据库中所有股票的收盘数据"""
        df_a = pd.DataFrame()
        for stock in self.stocks:
            sql = f'select Date,"Adj Close" from {stock["sql_table"]} where Date>="{start}" and Date<"{end}"'
            df = pd.read_sql(sql, self.db_engine, index_col='Date', parse_dates='Date')
            df_a[stock['name']] = df['Adj Close']

        return df_a
