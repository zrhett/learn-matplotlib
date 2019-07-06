import tkinter as tk
from tkinter import ttk
from . import views as v
from . import models as m


class AppWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('Matplotlib')
        self.__center_window(1200, 500)
        self.withdraw()
        self.protocol('WM_DELETE_WINDOW', self._destroyWindow)

        self.start_date, self.end_date = ('2018-01-01', '2019-01-01')

        self.data_model = m.DataModel()
        self.settings = {}
        self.callbacks = {}
        self.view = v.StockView(self, self.settings, self.callbacks)
        self.view.pack(padx=5, pady=5, expand=tk.YES, fill=tk.BOTH)
        self.view.plot(self.prepare_data(), self.start_date, self.end_date)

        self.deiconify()


    def __center_window(self, width, height):
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(size)

    def _destroyWindow(self):
        self.view.clear()
        self.quit()
        self.destroy()

    def prepare_data(self):
        stocks = self.data_model.read_all_stocks_to_dict(self.start_date, self.end_date)

        df_a = None
        for stock in stocks:
            df = stock['data'][['Close']]
            df.rename(columns={'Close': stock['name']}, inplace=True)
            if df_a is None:
                df_a = df
            else:
                df_a = df_a.join(df)

        return stocks, df_a
