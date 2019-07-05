import tkinter as tk
from tkinter import filedialog, messagebox
from time import time, sleep
import queue
import os
import threading

from .images import CREDIT_LOGO_24, CREDIT_LOGO_48
from .tools import time_interval_to_human
from .networks import CreditBot
from . import views as v
from . import models as m


class AppWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title('企业信用查询工具')
        self.__center_window(800, 500)
        self.resizable(width=False, height=False)
        self.total = 0
        self.is_continue = False
        self.is_running = False

        self.taskbar_icon = tk.PhotoImage(file=CREDIT_LOGO_48)
        self.call('wm', 'iconphoto', self._w, self.taskbar_icon)

        self.protocol('WM_DELETE_WINDOW', self._destroyWindow)

        self.__ui_msg_queue = queue.Queue()
        self.settings = {}
        self.callbacks = {
            'on_select_name_list': self.on_select_name_list,
            'on_query': self.on_query
        }

        self.view = v.QueryView(self, self.settings, self.callbacks)
        self.view.pack(padx=5, pady=5, expand=tk.YES, fill=tk.BOTH)
        self.data_model = m.GUIDataModel()