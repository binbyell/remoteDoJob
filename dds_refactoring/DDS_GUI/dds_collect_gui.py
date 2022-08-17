import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from DDS_GUI import gui_view_class as custom_gui
from DDS_GUI import gui_button
import queue
import time
from tcp import TcpSocket


quit_value = 1


class Application(ttk.Frame):
    master: tk.Tk
    # mainCanvas: tk.Canvas
    # scrollAbleFrame: ttk.Frame
    mainCanvas: custom_gui.ScrollableFrameCanvas
    frameFormDict = dict()
    nameRoot = ""

    def __init__(self, master=None):
        self.master = master
        self.master.geometry("640x400+100+100")
        super().__init__(self.master)
        self.create_menu()
        self.create_view()
        self.pack()

    def create_menu(self):
        # 메뉴 생성
        menubar = tk.Menu(self.master)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Save", command=self.fun_save)
        filemenu.add_command(label="Save as...", command=self.fun_save_as)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.fun_quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.master.config(menu=menubar)

    def create_view(self):
        # self.mainCanvas = tk.Canvas(self)
        self.mainCanvas = custom_gui.ScrollableFrameCanvas(self)
        scrollbar = ttk.Scrollbar(self.mainCanvas, orient="vertical", command=self.mainCanvas.yview)

        self.mainCanvas.configure(yscrollcommand=scrollbar.set)

        for i in range(4):
            # ttk.Label(self.mainCanvas.get_scrollable_frame(), text="Sample scrolling label").pack()
            frame_form = custom_gui.FrameForm(self.mainCanvas.get_scrollable_frame(), i)
            self.frameFormDict[custom_gui.tag_index_to_name(i)] = frame_form
            frame_form.get_frame().pack()

        self.mainCanvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        gui_button.ButtonFrame(self).pack(side='right')

    # 메인스레드, 보조스레드 종료
    def fun_quit(self):
        global quit_value
        quit_value = 0
        self.master.destroy()

    # menu_bar-file-save 기능함수
    def fun_save(self):
        filename = self.nameRoot
        if filename == '.txt':
            self.fun_save_as()
        elif filename[len(filename) - 3:] == 'txt':
            with open(filename, 'w') as f:
                f.write(self.frameFormDict[custom_gui.NameTag.name_1].get_text.text.get("1.0", "end-1c"))
                f.close()
        else:
            self.fun_save_as()

    # menu_bar-file-saveas 기능함수
    def fun_save_as(self):
        filename = self.nameRoot

        # 저장위치를 사용자가 임의로 정할 수 있도록 돕는 코드
        filename = filedialog.asksaveasfilename(initialdir="/", title="select file",
                                                filetypes=(("text files", "*.txt"),
                                                           ("all files", "*.*")))
        if filename == '':
            return 0

        # 저장시 자동으로 .txt
        filename = filename + '.txt'

        # 저장
        with open(filename, 'w') as f:
            f.write(self.frameFormDict[custom_gui.NameTag.name_1].get_text.text.get("1.0", "end-1c"))
            f.close()


# [x]버튼으로 종료시 정상적으로 보조스레드까지 종료시킬 수 있는 기능의 코드
def do_something():
    global quit_value
    quit_value = 0
    root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', do_something)
    app = Application(master=root)
    root.mainloop()
