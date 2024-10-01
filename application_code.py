import json
import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter.ttk import Label, OptionMenu, Button
from tkinter import messagebox as mb
import socket
import time


class ApplicationWindow:
    def __init__(self, mode: int) -> None:
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

        self.server_ip = None

        if mode:
            self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_sock.bind(('', 53210))
            self.server_sock.listen(1)
            threading.Thread(target=self.serv_connect, daemon=True).start()
        else:
            self.client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            udp_sock.bind(('', 37021))

            while not self.server_ip:
                data, addr = udp_sock.recvfrom(1024)
                message = data.decode('utf-8')
                if message.startswith('SERVER_IP:'):
                    self.server_ip = message.split(':')[1]
                    print(message)
                    time.sleep(1)

            if self.server_ip:
                self.client_sock.connect((self.server_ip, 53210))
                self.connect = True
                threading.Thread(target=self.import_drawing, daemon=True).start()

        self.root.mainloop()

        if self.connect:
            self.connect = False
            if mode:
                self.server_sock.close()
            else:
                self.client_sock.close()

    def serv_connect(self) -> None:
        self.broadcast_event = threading.Event()

        self.broadcast_thread = threading.Thread(target=self.broadcast_ip, daemon=True)
        self.broadcast_thread.start()

        self.client_sock, client_addr = self.server_sock.accept()
        self.connect = True
        threading.Thread(target=self.import_drawing, daemon=True).start()
        time.sleep(1)

        self.broadcast_event.set()

        if self.broadcast_thread.is_alive():
            self.broadcast_thread.join()

    def broadcast_ip(self):
        broadcast_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        broadcast_sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        server_ip = socket.gethostbyname(socket.gethostname())
        broadcast_message = f'SERVER_IP:{server_ip}'.encode('utf-8')

        while not self.broadcast_event.is_set():
            broadcast_sock.sendto(broadcast_message, ('<broadcast>', 37021))
            print(f'Broadcasting server IP: {server_ip}')
            self.broadcast_event.wait(1)

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
        if not btn:
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
