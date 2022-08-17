#클라이언트 코드
import socket
import threading
import tkinter as tk
import datetime


clId = "T1"


class SocketMsg:
    ok: str = "OK"
    collection_complete: str = "collection complete"
    interpolation_complete: str = "interpolation complete"
    fine_dust_prediction_request: str = "fine dust prediction request"
    fine_dust_prediction_complete: str = "fine dust prediction complete"


def send_msg_while(soc, msg: str = "OK"):
    while True:
        # msg = f"{clId}!/send_msg!{msg}"
        soc.sendall(msg.encode(encoding='utf-8'))
        if msg == '/stop':
            break
    print('클라이언트 메시지 입력 쓰레드 종료')


def send_msg(soc, msg: str = "OK"):
    soc.sendall(msg.encode(encoding='utf-8'))


def recv_msg(soc, app):
    while True:
        try:
            data = soc.recv(1024)
            msg = data.decode()
            strMsg = str(msg)
            strMsg = strMsg.strip()
            print(f"recv_msg : {strMsg}")

            if strMsg == SocketMsg.interpolation_complete or strMsg == SocketMsg.fine_dust_prediction_complete:
                soc.sendall(SocketMsg.ok.encode(encoding='utf-8'))

            if msg == '/stop':
                break
        except ConnectionResetError:
            app.text.insert(tk.END, "ConnectionResetError\n")
            print("ConnectionResetError")
            break
    soc.close()
    print('클라이언트 리시브 쓰레드 종료')


class Client(threading.Thread):
    # ip = 'localhost'
    ip = '127.0.0.1'
    port = 8092

    def __init__(self, app=None):
        threading.Thread.__init__(self)
        self.client_soc = None
        self.app = app

    def conn(self):
        try:
            self.client_soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_soc.connect((Client.ip, Client.port))
        except ConnectionRefusedError:
            print(f"Connection failed\nip:{self.ip}")
            return False

        msg = f"ip: {self.ip} linked\n"
        if self.app is not None:
            self.app.text.insert(tk.END, msg)
        else:
            print(msg)
        return True

    def run(self):

        # connect
        start_time = datetime.datetime.now()
        is_connect = self.conn()
        while not is_connect:
            self.app.text.insert(tk.END, f"{datetime.datetime.now().strftime('%m/%d  %H:%M:%S')}\n")
            if datetime.datetime.now() > start_time + datetime.timedelta(seconds=5):
                # self.app.root.destroy()
                self.app.text.insert(tk.END, "tcp link thread break.\n")
                break
            is_connect = self.conn()

        if is_connect:
            recv = threading.Thread(target=recv_msg, args=(self.client_soc, self.app,))
            recv.start()

    def send_msg_(self, msg):
        print(f"send msg : {msg}")
        t = threading.Thread(target=send_msg, args=(self.client_soc, msg))
        t.start()


if __name__ == '__main__':
    c = Client()
    c.run()

    c.send_msg_(SocketMsg.collection_complete)
