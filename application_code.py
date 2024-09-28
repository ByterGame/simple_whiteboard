import json
import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter.ttk import Label, OptionMenu, Button
from tkinter import messagebox as mb
import socket
import time


class ApplicationWindow:
    def __init__(self, mode: int, host_name: str) -> None:
        self.root = Tk()
        self.load_ui()

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = Canvas(self.root, bg='white', height=self.screen_height, width=self.screen_width)
        self.color_canvas = Canvas(self.root, bg='black', height=20, width=80)

        self.choose_size = StringVar(self.root)
        self.bind_actions()
        self.spawn_buttons()

        self.col = '#000000'
        self.prev_x, self.prev_y = 0, 0

        self.connect = False

        if mode:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
            self.server_sock.bind(('', 55555))
            self.server_sock.listen(1)
            threading.Thread(target=self.wait_connect, daemon=True).start()
        else:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((host_name, 55555))
            self.connect = True

        threading.Thread(target=self.import_drawing, daemon=True).start()

        self.root.mainloop()

        if self.connect:
            self.connect = False
            if mode:
                self.server_sock.close()
            else:
                self.client_sock.close()

    def wait_connect(self) -> None:
        self.client_sock, client_addr = self.server_sock.accept()
        self.connect = True

    def export_drawing(self, data: list) -> None:
        export_data = (json.dumps(data)).ljust(60)
        self.client_sock.send(export_data.encode())

    def import_drawing(self) -> None:
        while True:
            if self.connect:
                try:
                    import_data = json.loads(self.client_sock.recv(60).decode())
                    event = import_data[0]
                    match event:
                        case 0:
                            self.draw(*import_data[1:])
                        case 1:
                            self.canvas.config(bg=import_data[1])
                        case 2:
                            self.canvas.config(bg='white')
                            self.canvas.delete("all")
                except WindowsError:
                    self.connect = False
                    mb.showinfo('Оповещение', 'Клиент или сервер разорвал соединение!')
                    self.root.destroy()
                    pass
            else:
                time.sleep(0.05)

    def on_click(self, event: tk.Event, btn: int) -> None:
        size = int(self.choose_size.get())
        if btn == 0:
            col = self.col
        else:
            col = self.canvas["background"]
        x, y = event.x, event.y
        dist = ((x - self.prev_x) ** 2 + (y - self.prev_y) ** 2) ** 0.5

        if (self.prev_x + self.prev_y != 0) and dist > 2:
            self.draw(size, x, y, self.prev_x, self.prev_y, col)
            if self.connect:
                self.export_drawing([0, size, x, y, self.prev_x, self.prev_y, col])

            self.prev_x, self.prev_y = x, y

        elif (self.prev_x + self.prev_y) == 0:
            self.prev_x, self.prev_y = x, y

            self.draw(size, x, y, x, y, col)
            if self.connect:
                self.export_drawing([0, size, x, y, self.prev_x, self.prev_y, col])

        if event.type == "5":
            self.prev_x, self.prev_y = 0, 0

    def draw(self, size: int, x: int, y: int, px: int, py: int, col: str):
        if x == px and y == py:
            px, py = x + 1, y + 1
        self.canvas.create_polygon(x, y,
                                   px, py, fill=col, outline=col,
                                   width=size)

    def fill(self) -> None:
        self.canvas.config(bg=self.col)
        self.export_drawing([1, self.col])

    def delete(self) -> None:
        self.canvas.config(bg='white')
        self.canvas.delete("all")
        self.export_drawing([2, self.col])

    def color(self) -> None:
        col = colorchooser.askcolor()[1]
        if col:
            self.col = str(col)
            self.color_canvas.config(bg=self.col)

    def load_ui(self) -> None:
        self.root.geometry("1200x800")
        self.root.title('S1mple Whiteboard')

    def bind_actions(self) -> None:
        self.canvas.bind('<B1-Motion>', lambda event, a=10: self.on_click(event, 0))
        self.canvas.bind("<ButtonRelease-1>", lambda event, a=10: self.on_click(event, 0))
        self.canvas.bind('<Button-1>', lambda event, a=10: self.on_click(event, 0))

        self.canvas.bind('<B3-Motion>', lambda event, a=10: self.on_click(event, 1))
        self.canvas.bind("<ButtonRelease-3>", lambda event, a=10: self.on_click(event, 1))
        self.canvas.bind('<Button-3>', lambda event, a=10: self.on_click(event, 1))

    def spawn_buttons(self) -> None:
        size_list = OptionMenu(self.root, self.choose_size, '5', *[str(_) for _ in range(5, 51, 5)])
        color_btn = tk.ttk.Button(self.root, text='Выбрать цвет', command=self.color)
        clear_btn = tk.ttk.Button(self.root, text='Очистить всё', command=self.delete)
        fill_btn = tk.ttk.Button(self.root, text='Заливка', command=self.fill)
        size_label = tk.ttk.Label(self.root, text='Размер кисти')

        self.canvas.place(x=0, y=70)
        self.color_canvas.place(x=1000, y=35)
        color_btn.place(x=1000, y=10)
        clear_btn.place(x=240, y=40)
        fill_btn.place(x=240, y=10)
        size_label.place(x=900, y=10)
        size_list.place(x=950, y=35)
