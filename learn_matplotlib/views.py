import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import dates


class StockView(tk.Frame):
    colors = ['#5284C4', '#DA4453', '#42B498', '#8A79B5',
              '#3BADD9', '#F5BA41', '#8CBF51', '#D570A8']

    def __init__(self, parent, settings, callbacks, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.settings = settings
        self.callbacks = callbacks

        self.n_value = tk.IntVar()
        self.n_label = tk.StringVar()
        self.last_n = tk.IntVar()
        self.colorbar = None
        self.build_view()

    def build_view(self):
        self.fig = Figure(figsize=(12, 5), facecolor='white')
        self.axis_t = self.fig.add_subplot(221)
        self.axis_v = self.fig.add_subplot(223)
        self.axis_c = self.fig.add_subplot(122)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    # def update_figure(self, last_n):
    #     start_date = '2018-01-01'
    #     end_date = '2018-12-31'
    #
    #     current_n = self.n_value.get()
    #     if current_n == last_n.get():
    #         return
    #
    #     last_n.set(current_n)
    #     print(current_n)
    #     start_date = f'2018-{current_n:0>2}-01'
    #     n_label.set(f'周期：{start_date} 至 {end_date}')
    #     axis_t.clear()
    #     axis_c.clear()
    #     plot_trend(axis_t, stocks, start_date, end_date, y_limit)
    #     plot_corr(axis_c, df_a, start_date, end_date, colorbar)
    #     fig.canvas.draw()
    #
    #     label = ttk.Label(root, textvariable=n_label)
    #     label.pack(after=fig.canvas.get_tk_widget())
    #
    #     n_slider = ttk.Scale(master=root, variable=n_value, from_=1,
    #                          to=12, orient=tk.HORIZONTAL, length=int(fig.bbox.width),
    #                          command=lambda i: update(last_n))
    #     n_value.set(1)
    #     n_label.set(f'周期：{start_date} 至 {end_date}')
    #     n_slider.pack(after=label)

    def plot(self, data, start_date, end_date):
        stocks, df_a = data
        self.plot_trend(stocks, start_date, end_date)
        self.plot_corr(df_a, start_date, end_date)
        self.update()

    def plot_trend(self, stocks, start_date, end_date):
        y_limit = CalYTicksLimit()
        for i, stock in enumerate(stocks):
            df = stock['data']
            df = df[start_date: end_date]
            line = self.axis_t.plot(df['Close'], label=stock['name'], alpha=1.0, c=self.colors[(i + 0) % 8])
            max = df['Close'].max()
            max_idx = df['Close'].idxmax()
            min = df['Close'].min()
            min_idx = df['Close'].idxmin()
            y_limit.set(min, max)

            color = line[0].get_color()
            self.axis_t.annotate(f'Max={max:.2f}', xy=(max_idx, max), xytext=(0, 20), color=color,
                          xycoords='data', textcoords='offset points', ha='center', va='bottom',
                          arrowprops=dict(arrowstyle="-|>", color=color,
                                          connectionstyle='arc3,rad=0.2'))
            self.axis_t.annotate(f'Min={min:.2f}', xy=(min_idx, min), xytext=(0, -20), color=color,
                          xycoords='data', textcoords='offset points', ha='center', va='top',
                          arrowprops=dict(arrowstyle="-|>", color=color,
                                          connectionstyle='arc3,rad=0.2'))
        # self.axis_t.spines['left'].set_position(('outward', 0))
        # self.axis_t.spines['bottom'].set_position(('outward', 20))
        self.axis_t.spines['right'].set_visible(False)
        self.axis_t.spines['top'].set_visible(False)
        # self.axis_t.xaxis.set_ticks_position('bottom')
        # self.axis_t.xaxis.set_major_locator(dates.MonthLocator(interval=1))
        # self.axis_t.xaxis.set_major_formatter(dates.DateFormatter('%b'))
        self.axis_t.set_ylim(y_limit.get_min() - 300, y_limit.get_max() + 300)
        self.axis_t.set_xlabel('Date')
        self.axis_t.set_ylabel('Price')
        self.axis_t.legend()
        # self.axis_t.grid(linestyle='-')  # solid grid lines

    def plot_corr(self, df_a, start_date, end_date):
        corr = df_a[start_date: end_date].corr()
        corimage = self.axis_c.imshow(corr, cmap='OrRd', alpha=0.75)

        if self.colorbar is None:
            self.colorbar = self.fig.colorbar(corimage, ax=self.axis_c)
        else:
            self.colorbar.update_normal(corimage)

        self.axis_c.set(xticks=range(len(corr)), yticks=range(len(corr)))
        self.axis_c.set_xticklabels(corr.columns)
        self.axis_c.set_yticklabels(corr.columns)

    def clear(self):
        self.fig.clear()


class CalYTicksLimit():
    """计算yticks的上下边界"""
    def __init__(self):
        self.s_max = float('-inf')
        self.s_min = float('inf')

    def set(self, min, max):
        self.s_max = max if max > self.s_max else self.s_max
        self.s_min = min if min < self.s_min else self.s_min

    def get_min(self):
        return self.s_min

    def get_max(self):
        return self.s_max
