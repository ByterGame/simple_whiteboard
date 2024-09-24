import tkinter as tk
from tkinter import Tk
from tkinter.ttk import Button
from application_code import ApplicationWindow


class StartWindow:
    def __init__(self) -> None:
        self.root = Tk()
        self.root.geometry("350x128")

        self.spawn_buttons()

        self.root.mainloop()

    def start_server(self) -> None:
        self.root.destroy()
        ApplicationWindow()

    def start_client(self) -> None:
        self.root.destroy()
        ApplicationWindow()

    def spawn_buttons(self) -> None:
        server_btn = tk.ttk.Button(self.root, text='Захостить', command=self.start_server)
        client_btn = tk.ttk.Button(self.root, text='Подключиться', command=self.start_client)

        server_btn.grid(row=0, column=0, ipady=50, ipadx=50)
        client_btn.grid(row=0, column=1, ipady=50, ipadx=50)


StartWindow()
