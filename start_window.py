import threading
import tkinter as tk
from tkinter import Tk
from tkinter.ttk import Button
from application_code import ApplicationWindow
from client_code import Client
from server_code import Server


def start_application() -> None:
    ApplicationWindow()


class StartWindow:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.geometry("350x128")
        self.root.title('S1mple Whiteboard')
        self.root.resizable(False, False)

        self.server_btn = tk.ttk.Button(self.root, text='Захостить', command=self.start_server)
        self.client_btn = tk.ttk.Button(self.root, text='Подключиться', command=self.start_client)
        self.host_name_edit = tk.ttk.Entry(font=("Calibri 16"))
        self.connect_btn = tk.ttk.Button(self.root, text='Подключиться', command=self.connect)

        self.server_btn.grid(row=0, column=0, ipadx=50, ipady=50)
        self.client_btn.grid(row=0, column=1, ipadx=50, ipady=50)

        self.root.mainloop()

    def start_server(self) -> None:
        self.root.destroy()
        t2 = threading.Thread(target=start_application)
        t2.start()
        Server()
        t2.join()

    def start_client(self) -> None:
        self.server_btn.destroy()
        self.client_btn.destroy()
        self.host_name_edit.grid(ipadx=80, ipady=20)
        self.connect_btn.grid(ipadx=100, ipady=20)

    def connect(self):
        if self.host_name_edit.get():
            host_name = self.host_name_edit.get()
            self.root.destroy()
            t2 = threading.Thread(target=start_application)
            t2.start()
            Client(host_name)
            t2.join()
