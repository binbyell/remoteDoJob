import threading
import tkinter as tk
from tkinter import *
from tkinter import filedialog
import time
from time import sleep
import datetime
import queue
from dateutil.relativedelta import relativedelta
from datetime import datetime, timedelta
import os.path

from collect import collect_wind
from collect import collect_wind_first
from collect import collect_vssl
from collect import collect_dust
from collect import collect_dust_first
from collect import collect_traffic
from tcp import SocketClient
from tcp import SocketMsg
import Public.Common as Common
import os.path

collection_delay = 1
check_min = 50
quit_value = 1
filename = ""

"""
프로그램 실행시 바로 수집 시작.
메인 : Application 실행
ThreadTest : 보조 스레드, csv파일 수집.

수집
- 첫실행
- 매일 12시(정오, 자정)

global collection_delay
3600 = 1시간
60 = 1분
"""


class DDSCollect(threading.Thread):
    def __init__(self, application):
        threading.Thread.__init__(self)
        self.app = application

    def run(self):
        global quit_value
        global collection_delay

        print(f"quit_value: {quit_value}")
        self.dds_collect()
        while quit_value:
            sleep(collection_delay)

            if datetime.now().strftime('%M:%S') == "50:10":
                self.dds_collect()

    def dds_collect(self):
        self.app.text.insert(tk.END, f"{datetime.now().strftime('%M:%S')}\n")
        app.text.insert(tk.END, "----------start----------\n")
        # dds_collect_wind(self.app)
        # dds_collect_dust(self.app)
        dds_collect_vssl(self.app)
        # dds_collect_traffic(self.app)
        app.text.insert(tk.END, "----------end----------\n")


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.root = master
        self.pack()

        self.text = tk.Text(self)

        self.create_widgets()
        self.q = queue.Queue(10)

        self.t2 = SocketClient.Client(app=self)
        self.collect_thread = DDSCollect(self)
        # window 창 크기 고정
        self.root.resizable(0, 0)
        self.tcp_thread()
        self.collect()

    def create_widgets(self):
        self.root.title("dds 데이터 수집 모듈")

        self.text.insert(tk.END, "")
        self.text.pack(side="left", fill="both")

        scroll_y = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        scroll_y.pack(side="left", fill="both")

        self.text.configure(yscrollcommand=scroll_y.set)

        tcpTestButton = tk.Button()
        tcpTestButton.config(width=5, text="Link", command=self.tcp_thread)
        tcpTestButton.pack(side="bottom")

        # 메뉴 생성
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar)
        filemenu.add_command(label="Save", command=self.funSave)
        filemenu.add_command(label="Save as...", command=self.funSaveas)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.funQUIT)
        menubar.add_cascade(label="File", menu=filemenu)
        self.root.config(menu=menubar)

    def tcp_thread(self):
        print("tcp_thread")
        self.t2 = SocketClient.Client(app=self)
        self.t2.daemon = True
        self.t2.start()

    def collect(self):
        self.collect_thread.daemon = True
        self.collect_thread.start()
        self.t2.send_msg_(SocketClient.SocketMsg.collection_complete)
        ...

    def tcp_send(self):
        self.t2.send_msg_(SocketClient.SocketMsg.collection_complete)

    def fun_text_insert(self, txt: str):
        self.text.insert(tk.END, txt)

    # 메인스레드, 보조스레드 종료
    def funQUIT(self):
        global quit_value
        quit_value = 0
        self.master.destroy()

    # menu_bar-file-save 기능함수
    def funSave(self):
        global filename
        if filename == '.txt':
            self.funSaveas()
        elif filename[len(filename) - 3:] == 'txt':
            with open(filename, 'w') as f:
                f.write(self.text.get("1.0", "end-1c"))
                f.close()
        else:
            self.funSaveas()

    # menu_bar-file-saveas 기능함수
    def funSaveas(self):
        global filename

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
            f.write(self.text.get("1.0", "end-1c"))
            f.close()


def dds_collect_wind(application: Application):
    init = Common.InitDict(Common.Tag.wind)
    path = init.FolderPath

    application.fun_text_insert(f"wind_data_start  =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    if os.path.isdir(path):
        collect_wind.get_wind()
    else:
        collect_wind_first.get_wind_1st()
    application.fun_text_insert(f"wind_data_end    =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    ...


def dds_collect_dust(application: Application):
    init = Common.InitDict(Common.Tag.dust)
    path = init.FolderPath

    application.fun_text_insert(f"dust_data_start  =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    if os.path.isdir(path):
        collect_dust.get_dust()
    else:
        collect_dust_first.get_dust_1st()
    application.fun_text_insert(f"dust_data_end    =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    ...


def dds_collect_vssl(application: Application):
    application.fun_text_insert(f"vssl_data_start  =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    collect_vssl.get_vssl_with_check_1st()
    application.fun_text_insert(f"vssl_data_end    =======  {datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
    ...


def dds_collect_traffic(application: Application):
    ...


# [x]버튼으로 종료시 정상적으로 보조스레드까지 종료시킬 수 있는 기능의 코드
def quit_with_x_button():
    global quit_value
    print("quit_with_x_button")
    quit_value = 0
    root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    root.protocol('WM_DELETE_WINDOW', quit_with_x_button)
    app = Application(master=root)
    app.mainloop()
    ...
