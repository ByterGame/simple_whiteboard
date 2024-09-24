import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter.ttk import Label, OptionMenu, Button


class ApplicationWindow:
    def __init__(self):
        self.root = Tk()
        self.root.geometry("1280x720")
        self.root.title('S1mple Whiteboard')

        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()

        self.cn = Canvas(self.root, bg='black', height=20, width=80)
        self.canvas = Canvas(self.root, bg='white', height=self.screen_height, width=self.screen_width)

        self.col = '#000000'
        self.prev_x, self.prev_y = 0, 0

        self.choose_size = StringVar(self.root)
        self.spawn_buttons()

        t2 = threading.Thread(target=self.import_drawing, daemon=True)
        t2.start()

        self.root.mainloop()

        with open('export_message', 'w') as em:
            em.write('close_socket')
        with open('import_message', 'w'):
            pass

    def draw(self, event) -> None:
        size = self.choose_size.get()
        x, y = event.x, event.y
        dist = ((x - self.prev_x) ** 2 + (y - self.prev_y) ** 2) ** 0.5
        if (self.prev_x + self.prev_y != 0) and dist > 5:
            self.canvas.create_polygon((x, y),
                                       (self.prev_x, self.prev_y), fill=self.col, outline=self.col, width=size)

            self.export_drawing(size, x, y, self.prev_x, self.prev_y)
            self.prev_x, self.prev_y = x, y

        elif (self.prev_x + self.prev_y) == 0:
            self.prev_x, self.prev_y = x, y
            self.canvas.create_polygon((x, y),
                                       (self.prev_x, self.prev_y), fill=self.col, outline=self.col,
                                       width=str(int(size) * 0.5))

            self.export_drawing(size, x, y, self.prev_x, self.prev_y)

        if event.type == "5":
            self.prev_x, self.prev_y = 0, 0

    def export_drawing(self, size, x, y, px, py) -> None:
        with open('export_message', 'a') as import_file:
            export_data = [self.col, str(size), str(x), str(y), str(px), str(py)]
            export_string = (' '.join(export_data) + ' ' + '0' * 15)[:30]
            import_file.write(export_string + '\n')

    def import_drawing(self) -> None:
        while True:
            with open('import_message', 'r+') as file_read:
                import_string = file_read.readline().strip()
                import_data = import_string.split()
                while import_data:
                    brush_color = import_data[0]
                    try:
                        brush_size, x, y, px, py = list(map(int, import_data[1:6]))
                        self.canvas.create_polygon((x, y), (px, py), fill=brush_color, outline=brush_color,
                                                   width=brush_size)
                    finally:
                        pass
                    import_string = file_read.readline().strip()
                    import_data = import_string.split()
                file_read.truncate(0)

    def fill(self) -> None:
        self.canvas.config(bg=self.col)

    def delete(self) -> None:
        self.canvas.config(bg='white')
        self.canvas.delete("all")

    def color(self) -> None:
        self.col = str(colorchooser.askcolor()[1])
        self.cn.config(bg=self.col)

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
        self.cn.place(x=1000, y=35)
