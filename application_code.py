import threading
import tkinter
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


def draw(event) -> None:
    size = choose_size.get()
    canvas.create_oval((event.x - int(size) // 2, event.y - int(size) // 2),
        (event.x + int(size) // 2, event.y + int(size) // 2), fill=col, outline=col)

    with open('export_massage', 'w') as file_write:
        export_data = [col, str(size), str(event.x), str(event.y)]
        file_write.write(' '.join(export_data))



def import_drawing() -> None:
    while True:
        with open('import_massage', 'r') as file_read:
            import_data = file_read.readline().split()
            if import_data:
                brush_color = import_data[0]
                brush_size, x, y = list(map(int, import_data[1:]))

                canvas.create_oval((x - brush_size // 2, y - brush_size // 2),
                                   (x + brush_size // 2, y + brush_size // 2), fill=brush_color, outline=col)


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

size_list = OptionMenu(root, choose_size, '15', *[str(_) for _ in range(5, 101, 5)])
color_btn = tkinter.ttk.Button(root, text='Выбрать цвет', command=color)
clear_btn = tkinter.ttk.Button(root, text='Очистить всё', command=delete)
fill_btn = tkinter.ttk.Button(root, text='Заливка', command=fill)
size_label = tkinter.ttk.Label(root, text='Размер кисти')
name_label = tkinter.ttk.Label(root, text='Название файла:')
name_edit = tkinter.ttk.Entry()

canvas.bind("<B1-Motion>", draw)
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

t2 = threading.Thread(target=import_drawing)
t2.start()

root.mainloop()
