import json
import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter.ttk import Label, OptionMenu, Button
from tkinter import messagebox as mb
import socket
import time
from tkinter import PhotoImage


class ApplicationWindow:
    def __init__(self, mode: int, host_name: str) -> None:
        self.root = Tk()
        self.load_ui()
        self.mode = mode
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.canvas = Canvas(self.root, bg='white', height=self.screen_height, width=self.screen_width)
        self.color_canvas = Canvas(self.root, bg='black', height=20, width=80)

        self.choose_size = StringVar(self.root)
        self.bind_actions()
        self.spawn_buttons()

        self.col = '#000000'
        self.prev_x, self.prev_y = 0, 0

        self.client_count = 0
        self.wait_client = True
        self.state = list()
        self.clients = list()
        self.connect = False
        self.server_connect = False
        server_sock = None
        if mode:
            server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
            self.server_connect = True
            server_bg = PhotoImage(file='notification.png')
            self.canvas.create_image(600, 400, image=server_bg)
            server_sock.bind(('', 55555))
            server_sock.listen(10)
            threading.Thread(target=self.wait_client_connect, daemon=True, args=(server_sock, )).start()
            threading.Thread(target=self.send_state, daemon=True).start()
        else:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_sock.connect((host_name, 55555))
            self.connect = True
            threading.Thread(target=self.import_drawing, daemon=True).start()
        self.root.mainloop()

    def export_delta_for_server(self, data: list) -> None:
        try:
            export_data = (json.dumps(data)).ljust(100)
            self.client_sock.send(export_data.encode())
        except WindowsError:
            pass

    def wait_client_connect(self, server_sock):
        while self.client_count <= 3 and self.server_connect:
            if self.wait_client:
                self.wait_client = False
                threading.Thread(target=self.connect_client, daemon=True, args=(server_sock,)).start()

    def connect_client(self, server_sock):
        client_sock, client_addr = server_sock.accept()
        self.wait_client = True
        self.client_count += 1
        self.clients.append(client_sock)
        threading.Thread(target=self.wait_message_from_client(client_sock), daemon=True).start()

    def wait_message_from_client(self, client_sock):
        while client_sock and self.server_connect:
            try:
                data = json.loads(client_sock.recv(100).decode())
                event = data[0]
                match event:
                    case 1:
                        self.state.clear()
                    case 2:
                        self.state.clear()
                self.state.append(data)
            except WindowsError:
                client_sock.close()
                self.clients.remove(client_sock)
                self.client_count -= 1
                break

    def send_state(self):
        while self.server_connect:
            if self.state:
                state = self.state.pop(0)
                threading.Thread(target=self.cycle_send_state, daemon=True, args=(state, )).start()

    def cycle_send_state(self, state):
        for sock in self.clients:
            try:
                sock.send(json.dumps(state).ljust(100).encode())
            except ():
                pass

    def import_drawing(self) -> None:
        while not self.server_connect:
            if self.connect:
                try:
                    import_data = json.loads(self.client_sock.recv(100).decode())
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
                    mb.showinfo('Оповещение', 'Cервер разорвал соединение!')
                    self.root.destroy()
                    pass
            else:
                time.sleep(0.05)

    def on_click(self, event: tk.Event, btn: int) -> None:
        if not self.mode:
            size = int(self.choose_size.get())
            if btn == 0:
                col = self.col
            else:
                col = self.canvas["background"]
            x, y = event.x, event.y
            dist = ((x - self.prev_x) ** 2 + (y - self.prev_y) ** 2) ** 0.5

            if (self.prev_x + self.prev_y != 0) and dist > 10:
                self.draw(size, x, y, self.prev_x, self.prev_y, col)
                if self.connect:
                    self.export_delta_for_server([0, size, x, y, self.prev_x, self.prev_y, col])

                self.prev_x, self.prev_y = x, y

            elif (self.prev_x + self.prev_y) == 0:
                self.prev_x, self.prev_y = x, y

                self.draw(size, x, y, x, y, col)
                if self.connect:
                    self.export_delta_for_server([0, size, x, y, self.prev_x, self.prev_y, col])

            if event.type == "5":
                self.prev_x, self.prev_y = 0, 0

    def draw(self, size: int, x: int, y: int, px: int, py: int, col: str):
        if x == px and y == py:
            px, py = x + 1, y + 1
        self.canvas.create_polygon(x, y,
                                   px, py, fill=col, outline=col,
                                   width=size)

    def fill(self) -> None:
        # self.canvas.config(bg=self.col)
        self.export_delta_for_server([1, self.col])

    def delete(self) -> None:
        # self.canvas.config(bg='white')
        # self.canvas.delete("all")
        self.export_delta_for_server([2, self.col])

    def color(self) -> None:
        col = colorchooser.askcolor()[1]
        if col:
            self.col = str(col)
            self.color_canvas.config(bg=self.col)

    def load_ui(self) -> None:
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
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
