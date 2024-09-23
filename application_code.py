import threading
import tkinter as tk
from tkinter import Tk, Canvas, StringVar, colorchooser
from tkinter import messagebox as mbox
from tkinter.ttk import Label, OptionMenu

root = Tk()
root.geometry("1280x720")
root.title('Paint')

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

cn = Canvas(root, bg='black', height=20, width=80)
canvas = Canvas(root, bg='white', height=screen_height, width=screen_width)

col = '#000000'
prev_x, prev_y = 0, 0


def draw(event) -> None:
    global prev_x, prev_y
    size = choose_size.get()
    x, y = event.x, event.y
    dist = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5
    if (prev_x + prev_y != 0) and dist > 5:
        canvas.create_polygon((x, y),
                              (prev_x, prev_y), fill=col, outline=col, width=size)

        export_drawing(size, x, y, prev_x, prev_y)
        prev_x, prev_y = x, y

    elif (prev_x + prev_y) == 0:
        prev_x, prev_y = x, y
        canvas.create_polygon((x, y),
                              (prev_x, prev_y), fill=col, outline=col, width=str(int(size) * 0.5))

        export_drawing(size, x, y, prev_x, prev_y)

    if event.type == "5":
        prev_x, prev_y = 0, 0


def export_drawing(size, x, y, px, py) -> None:
    with open('export_massage', 'a') as import_file:
        export_data = [col, str(size), str(x), str(y), str(px), str(py)]
        export_string = (' '.join(export_data)+' '+'0'*15)[:30]
        import_file.write(export_string + '\n')


def import_drawing() -> None:
    while True:
        with open('import_massage', 'r+') as file_read:
            import_data = file_read.readline().split()
            while import_data:
                print(import_data)
                if import_data:
                    brush_color = import_data[0]
                    brush_size, x, y, px, py = list(map(int, import_data[1:7]))
                    canvas.create_polygon((x, y),
                                          (px, py), fill=brush_color, outline=brush_color,
                                          width=brush_size),
                import_data = file_read.readline().split()
            file_read.truncate(0)


def fill() -> None:
    global col
    canvas.config(bg=col)


def delete() -> None:
    canvas.config(bg='white')
    canvas.delete("all")


def color() -> None:
    global col
    col = str(colorchooser.askcolor()[1])
    cn.config(bg=col)


choose_size = StringVar(root)

size_list = OptionMenu(root, choose_size, '15', *[str(_) for _ in range(5, 51, 5)])
color_btn = tk.ttk.Button(root, text='Выбрать цвет', command=color)
clear_btn = tk.ttk.Button(root, text='Очистить всё', command=delete)
fill_btn = tk.ttk.Button(root, text='Заливка', command=fill)
size_label = tk.ttk.Label(root, text='Размер кисти')
name_label = tk.ttk.Label(root, text='Название файла:')
name_edit = tk.ttk.Entry()

canvas.bind('<B1-Motion>', draw)
canvas.bind("<ButtonRelease-1>", draw)
canvas.bind('<Button-1>', draw)

color_btn.place(x=1000, y=10)
name_label.place(x=10, y=10)
name_edit.place(x=110, y=10)
clear_btn.place(x=240, y=40)
fill_btn.place(x=240, y=10)
size_label.place(x=900, y=10)
size_list.place(x=950, y=35)
canvas.place(x=0, y=70)
cn.place(x=1000, y=35)

t2 = threading.Thread(target=import_drawing, daemon=True)
t2.start()

root.mainloop()

with open('export_massage', 'w') as em:
    em.write('close_socket\n')
with open('import_massage', 'w') as im:
    pass
