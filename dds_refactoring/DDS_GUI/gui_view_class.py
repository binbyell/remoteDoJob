import tkinter as tk
from tkinter import ttk

import threading


class NameTag:
    name_1 = 'wind'
    name_2 = 'dust'
    name_3 = 'vssl'
    name_4 = 'traffic'

    def tag_index(self, index: int):
        if index == 0:
            return self.name_1
        elif index == 1:
            return self.name_2
        elif index == 2:
            return self.name_3
        else:
            return self.name_4


def tag_index_to_name(index: int):
    if index == 0:
        return NameTag.name_1
    elif index == 1:
        return NameTag.name_2
    elif index == 2:
        return NameTag.name_3
    else:
        return NameTag.name_4


class FrameForm:
    thisFrame: tk.Frame
    thisText: tk.Text
    thisName: ttk.Label

    def __init__(self, main_frame=None, label: int = 0):
        # this_root.geometry("640x400+100+100")
        # , relief="solid", bd=2
        self.thisFrame = tk.Frame(main_frame)

        # self.startButton = tk.Button(self.thisFrame)
        # self.startButton.config(width=5, text="START", anchor='center')
        # self.startButton.pack(side="bottom")
        self.thisName = ttk.Label(self.thisFrame, text=NameTag.tag_index(NameTag(), index=label))
        self.thisName.pack(side='top', pady=10)

        self.thisText = tk.Text(self.thisFrame, width=60)

        scroll_y = tk.Scrollbar(self.thisFrame, orient="vertical", command=self.thisText.yview)
        # scroll_x = tk.Scrollbar(self.thisFrame, orient="horizontal", command=self.thisText.xview)

        # scroll_x.pack(side='bottom', fill='both')
        self.thisText.pack(side='left')
        scroll_y.pack(side='left', fill='both')

        self.thisText.configure(yscrollcommand=scroll_y.set)
        # self.thisText.configure(xscrollcommand=scroll_x.set)

    def get_frame(self):
        return self.thisFrame

    def get_text(self):
        return self.thisText

    def write_text(self, text: str):
        self.thisText.insert(tk.END, f"\n{text}")


class ScrollableFrameCanvas(tk.Canvas):
    master: tk.Tk
    scrollableFrame: ttk.Frame

    def __init__(self, master=None):
        self.master = master
        super().__init__(width=100, height=100)

        self.scrollableFrame = ttk.Frame(self)
        self.scrollableFrame.bind(
            "<Configure>",
            lambda e: self.configure(
                scrollregion=self.bbox("all")
            )
        )
        self.create_window((0, 0), window=self.scrollableFrame, anchor="nw")

    def get_scrollable_frame(self):
        return self.scrollableFrame
