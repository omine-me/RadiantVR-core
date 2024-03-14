import csv
from functools import partial

from tkinter import ttk
from tkinter import filedialog
import tkinter as tk

from main_from_file import main

file_header = []
file_data = []
file_name = ""
table_from_file = None
table_interactive = None

def open_file(root, table):
    global file_header, file_data, file_name
    file_name = filedialog.askopenfilename(initialdir='~/')
    if file_name:
        print(file_name)
        selected_filename.set(file_name)
        with open(file_name, "r") as f:
            # column names
            file_header = next(csv.reader(f))
            file_data = list(csv.reader(f))
            # print(file_data)
            try:
                table.destroy()
            except:
                pass
            try:
                table = generate_table(root)
            except IndexError as e:
                print(e)
                selected_filename.set(f"INVALID FILE: {file_name}")

def start():
    # print("start")
    # pass
    main(file_name)

def init():
    root = tk.Tk()
    root.title('Lights Controler')
    root.geometry("800x500")
    return root

def layout_for_from_file(root):
    global table_from_file
    # global selected_filename
    frame_from_file = tk.Frame(root)
    frame_from_file.pack(anchor=tk.W)

    frame_file_picker = tk.Frame(frame_from_file)
    frame_file_picker.pack(anchor=tk.W)

    Title1 = tk.Label(frame_file_picker, text='Run from file', font=("Helvetica", 20))
    Title1.pack(anchor=tk.W)
    # Open File
    file_picker_button = tk.Button(
        frame_file_picker, text='Open Csv File', width=15,
        command=partial(open_file, frame_from_file, table_from_file))
    file_picker_button.pack(side=tk.LEFT)
    selected_file_label = tk.Label(frame_file_picker, textvariable=selected_filename)
    selected_file_label.pack()

def layout_for_interactive(root):
    global table_interactive
    # global selected_filename
    frame_for_interactive = tk.Frame(root)
    frame_for_interactive.pack(anchor=tk.W)

    frame_file_picker = tk.Frame(frame_for_interactive)
    frame_file_picker.pack(anchor=tk.W)

    Title1 = tk.Label(frame_file_picker, text='Interactive run', font=("Helvetica", 20))
    Title1.pack(anchor=tk.W)
    # Open File
    file_picker_button = tk.Button(
        frame_file_picker, text='Edit in Excel', width=15,
        command=partial(open_file, frame_for_interactive, table_interactive))
    file_picker_button.pack(side=tk.LEFT)
    # selected_file_label = tk.Label(frame_file_picker, textvariable=selected_filename)
    # selected_file_label.pack()

def generate_table(root):
    # # Treeviewの生成
    frame_table = tk.Frame(root)
    frame_table.pack(anchor=tk.W)
    tree = ttk.Treeview(frame_table, columns=file_header if file_header else None)
    tree.delete(*tree.get_children())  # Clear existing data in the tree
    if True:#file_data:
        # 列の設定
        tree.column('#0',width=0, stretch='no')
        tree.column(file_header[0], anchor='center', width=80)
        tree.column(file_header[1], anchor='w', width=100)
        tree.column(file_header[2],anchor='w', width=100)
        tree.column(file_header[3], anchor='w', width=100)
        # 列の見出し設定
        tree.heading('#0',text='')
        tree.heading(file_header[0],text=file_header[0])
        tree.heading(file_header[1], text=file_header[1], anchor='center')
        tree.heading(file_header[2], text=file_header[2], anchor='w')
        tree.heading(file_header[3],text=file_header[3], anchor='center')
        # レコードの追加
        for row in file_data:
            tree.insert(parent='', index='end', values=row)
    # ウィジェットの配置
    tree.pack(side=tk.LEFT, anchor=tk.W, pady=10)
    start_button = tk.Button(
        frame_table, text='Start', width=15,
        command=start)
    start_button.pack(side=tk.LEFT, anchor=tk.S)

    return frame_table



if __name__ == "__main__":
    root = init()
    selected_filename = tk.StringVar(value="No file selected")

    layout_for_from_file(root)

    border = ttk.Separator(root, orient="horizontal").pack(fill="both", pady=20)

    layout_for_interactive(root)

    root.mainloop()