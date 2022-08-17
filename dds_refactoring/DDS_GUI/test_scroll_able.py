import tkinter as tk
from tkinter import ttk
import threading


def test_scrollable_frame():
    root = tk.Tk()
    container = ttk.Frame(root)
    canvas = tk.Canvas(container)
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set)

    for i in range(50):
        ttk.Label(scrollable_frame, text="Sample scrolling label").pack()
        # FrameForm(scrollable_frame).get_frame().pack()

    container.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    root.mainloop()


class ButtonFrame(ttk.Frame):

    master: tk.Tk
    buttonT: ttk.Button
    buttonA: ttk.Button
    button1: ttk.Button
    button2: ttk.Button
    button3: ttk.Button

    def __init__(self, master=None):
        self.master = master
        super().__init__(self.master)
        self.buttonT = ttk.Button(self, text='tcp', command=self.button_tcp_function())
        self.buttonT.pack(side='bottom')
        self.buttonA = ttk.Button(self, text='all', command=self.button_a_function())
        self.buttonA.pack(side='right', ipady=25)
        self.button1 = ttk.Button(self, text='1', command=self.button_1_function())
        self.button1.pack()
        self.button2 = ttk.Button(self, text='2', command=self.button_2_function())
        self.button2.pack()
        self.button3 = ttk.Button(self, text='3', command=self.button_3_function())
        self.button3.pack()

    def button_tcp_function(self):
        ...

    def button_a_function(self):
        self.button_1_function()
        self.button_2_function()
        self.button_3_function()

    def button_1_function(self):
        ...

    def button_2_function(self):
        ...

    def button_3_function(self):
        ...


if __name__ == '__main__':
    root = tk.Tk()
    test = ButtonFrame(root)
    test.pack()
    root.mainloop()
    ...
