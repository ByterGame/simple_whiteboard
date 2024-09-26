import json
import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter.ttk import Label, OptionMenu, Button
from fnmatch import fnmatch
import socket


class ApplicationWindow:
    def __init__(self, mode, host_name):
        self.root = Tk()
        self.load_ui()

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = Canvas(self.root, bg='white', height=self.screen_height, width=self.screen_width)
        self.color_canvas = Canvas(self.root, bg='black', height=20, width=80)

        self.col = '#000000'
        self.prev_x, self.prev_y = 0, 0

        self.choose_size = StringVar(self.root)

        self.spawn_buttons()
        self.connect = False
        if mode:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
            self.server_sock.bind(('', 55555))
            self.server_sock.listen(1)
            threading.Thread(target=self.wait_connect).start()
        else:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((host_name, 55555))
            self.connect = True

        threading.Thread(target=self.import_drawing, daemon=True).start()

        self.root.mainloop()
        self.on_close()

    def wait_connect(self) -> None:
        self.client_sock, client_addr = self.server_sock.accept()
        self.connect = True

    def export_drawing(self, size, x, y, px, py) -> None:
        export_data = (self.col, str(size), str(x), str(y), str(px), str(py))
        self.client_sock.sendall(json.dumps(export_data).encode())

    def import_drawing(self) -> None:
        while True:
            if self.connect:
                import_data = self.client_sock.recv(100000).decode().split('\n')
                threading.Thread(target=self.draw_import_points(import_data)).start()

    def draw_import_points(self, import_data) -> None:
        for line in import_data:
            print(line.strip())
            if fnmatch(line.strip(), '[[]*[]]'):
                line = json.loads(line)
                brush_color = line[0]
                brush_size, x, y, px, py = line[1:]
                self.canvas.create_polygon((x, y), (px, py), fill=brush_color, outline=brush_color,
                                           width=brush_size)

    def draw(self, event) -> None:
        size = int(self.choose_size.get())
        x, y = event.x, event.y
        dist = ((x - self.prev_x) ** 2 + (y - self.prev_y) ** 2) ** 0.5

        if (self.prev_x + self.prev_y != 0) and dist > 5:
            self.canvas.create_polygon((x, y),
                                       (self.prev_x, self.prev_y), fill=self.col, outline=self.col,
                                       width=size)
            if self.connect:
                self.export_drawing(size, x, y, self.prev_x, self.prev_y)
            self.prev_x, self.prev_y = x, y

        elif (self.prev_x + self.prev_y) == 0:
            self.prev_x, self.prev_y = x, y
            self.canvas.create_oval((x, y),
                                    (x, y), fill=self.col, outline=self.col,
                                    width=size * 0.85)
            if self.connect:
                self.export_drawing(size, x, y, self.prev_x, self.prev_y)

        if event.type == "5":
            self.prev_x, self.prev_y = 0, 0

    def fill(self) -> None:
        self.canvas.config(bg=self.col)

    def delete(self) -> None:
        self.canvas.config(bg='white')
        self.canvas.delete("all")

    def color(self) -> None:
        self.col = str(colorchooser.askcolor()[1])
        self.color_canvas.config(bg=self.col)

    def load_ui(self) -> None:
        self.root.geometry("1280x720")
        self.root.title('S1mple Whiteboard')
        self.root.resizable(False, False)

    def spawn_buttons(self) -> None:
        size_list = OptionMenu(self.root, self.choose_size, '15', *[str(_) for _ in range(5, 51, 5)])
        color_btn = tk.ttk.Button(self.root, text='Выбрать цвет', command=self.color)
        clear_btn = tk.ttk.Button(self.root, text='Очистить всё', command=self.delete)
        fill_btn = tk.ttk.Button(self.root, text='Заливка', command=self.fill)
        size_label = tk.ttk.Label(self.root, text='Размер кисти')

        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.draw)
        self.canvas.bind('<Button-1>', self.draw)

        color_btn.place(x=1000, y=10)
        clear_btn.place(x=240, y=40)
        fill_btn.place(x=240, y=10)
        size_label.place(x=900, y=10)
        size_list.place(x=950, y=35)
        self.canvas.place(x=0, y=70)
        self.color_canvas.place(x=1000, y=35)
