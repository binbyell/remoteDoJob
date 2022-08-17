import tkinter as tk
import threading
from tkinter import ttk
from DDS_GUI import gui_view_class as view_class
from DDS_GUI import dds_collect_gui
from collect import collect_vssl
from collect import collect_wind
from collect import collect_wind_first
from collect import collect_dust
from collect import collect_dust_first


class FunctionThread(threading.Thread):
    app: dds_collect_gui.Application

    def __init__(self, app, function, target: str):
        super().__init__()
        self.app = app
        self.function = function
        self.target = target

    def run(self):
        if self.target == view_class.NameTag.name_1:
            self.function(frame_form=self.app.frameFormDict[view_class.tag_index_to_name(0)])
        elif self.target == view_class.NameTag.name_2:
            self.function(frame_form=self.app.frameFormDict[view_class.tag_index_to_name(1)])
        elif self.target == view_class.NameTag.name_3:
            self.function(frame_form=self.app.frameFormDict[view_class.tag_index_to_name(2)])
        elif self.target == view_class.NameTag.name_4:
            self.function(frame_form=self.app.frameFormDict[view_class.tag_index_to_name(3)])
        ...


class ButtonFrame(ttk.Frame):

    master: tk.Tk
    checkFirst: tk.BooleanVar
    labelTcpCheck: ttk.Label
    checkBoxFirstCheck: tk.Checkbutton
    buttonT: ttk.Button
    buttonA: ttk.Button
    button1: ttk.Button
    button2: ttk.Button
    button3: ttk.Button
    button4: ttk.Button

    def __init__(self, master=None):
        self.master = master
        super().__init__(self.master)
        self.checkFirst = tk.BooleanVar()

        self.labelTcpCheck = ttk.Label(self, text="ip")
        self.labelTcpCheck.pack(side='top')
        self.checkBoxFirstCheck = tk.Checkbutton(
            self, variable=self.checkFirst, onvalue=True, offvalue=False, command=self.check_box_function, text="first")
        self.checkBoxFirstCheck.pack(side='top')

        self.buttonT = ttk.Button(self, text='tcp', command=self.button_tcp_function)
        self.buttonT.pack(side='bottom')

        self.buttonA = ttk.Button(self, text='all', command=self.button_a_function)
        self.buttonA.pack(side='right', ipady=36)

        self.button1 = ttk.Button(self, text=view_class.NameTag.name_1, command=self.button_1_function)
        self.button1.pack()

        self.button2 = ttk.Button(self, text=view_class.NameTag.name_2, command=self.button_2_function)
        self.button2.pack()

        self.button3 = ttk.Button(self, text=view_class.NameTag.name_3, command=self.button_3_function)
        self.button3.pack()

        self.button4 = ttk.Button(self, text=view_class.NameTag.name_4, command=self.button_4_function)
        self.button4.pack()

    def button_tcp_function(self):
        self.labelTcpCheck.config(text="tcp function")

    def check_box_function(self):
        # self.checkFirst =
        print(self.checkFirst.get())
        ...

    def button_a_function(self):
        self.button_1_function()
        self.button_2_function()
        self.button_3_function()
        self.button_4_function()

    # wind
    def button_1_function(self):
        job: threading.Thread
        if self.checkFirst.get():
            job = FunctionThread(self.master, function=collect_wind_first.get_wind_1st, target=view_class.NameTag.name_1)
        else:
            job = FunctionThread(self.master, function=collect_wind.get_wind, target=view_class.NameTag.name_1)
        job.start()

    # dust
    def button_2_function(self):
        job: threading.Thread
        if self.checkFirst.get():
            job = FunctionThread(self.master, function=collect_dust_first.get_dust_1st, target=view_class.NameTag.name_2)
        else:
            job = FunctionThread(self.master, function=collect_dust.get_dust, target=view_class.NameTag.name_2)
        job.start()

    # vssl
    def button_3_function(self):
        job: threading.Thread
        print(f"check : {self.master.frameFormDict}")
        if self.checkFirst.get():
            # job = threading.Thread(target=collect_vssl.get_vssl_with_check_1st, args=self.master.frameFormList[2])
            job = FunctionThread(self.master, function=collect_vssl.get_vssl_with_check_1st, target=view_class.NameTag.name_3)
        else:
            # job = threading.Thread(target=collect_vssl.get_vssl_with_check_1st, args=self.master.frameFormList[2])
            job = FunctionThread(self.master, function=collect_vssl.get_vssl_with_check_1st, target=view_class.NameTag.name_3)
        job.start()

    # traffic
    def button_4_function(self):
        ...
