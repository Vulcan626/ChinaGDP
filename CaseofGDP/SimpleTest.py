import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("中国GDP可视化")
        self.root.minsize(800, 600)
        self.root.configure(bg="white")

        self.sidebar_color = "#F0F0F0"
        self.content_color = "white"

        self.setup_sidebar()
        self.setup_content()

        self.active_button = None
        self.active_list = None

    def setup_sidebar(self):
        self.sidebar_frame = tk.Frame(self.root, width=200, bg=self.sidebar_color)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.sidebar_frame.pack_propagate(False)

        self.functions_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color)
        self.functions_frame.pack(fill=tk.X, pady=(0, 20))
        self.create_functions()

        self.list_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color, highlightbackground="white")  # 将highlightbackground设为白色
        self.list_frame.pack(fill=tk.BOTH, expand=True)

    def create_functions(self):
        function_names = ["总GDP趋势图", "地区GDP对比", "各省份GDP趋势图", "各省份GDP分布图"]
        for idx, name in enumerate(function_names):
            button = ttk.Button(
                self.functions_frame, text=name, style='Light.TButton',
                command=lambda idx=idx: self.toggle_list(idx)
            )
            button.pack(fill=tk.X, padx=5, pady=5)

    def toggle_list(self, idx):
        if self.active_button and self.active_button == self.functions_frame.winfo_children()[idx]:
            return

        if self.active_list:
            self.active_list.destroy()

        if idx == 2:
            self.create_years_list()
        elif idx == 3:
            self.create_provinces_list()
        else:
            self.active_button = None

    def create_provinces_list(self):
        self.active_button = self.functions_frame.winfo_children()[3]
        self.active_list = tk.Listbox(self.list_frame, bg=self.sidebar_color, fg='black', highlightbackground="white")  # 将highlightbackground设为白色
        self.active_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        provinces = ["省份1", "省份2", "省份3", "省份4", "...", "省份N"]
        for province in provinces:
            self.active_list.insert(tk.END, province)

    def create_years_list(self):
        self.active_button = self.functions_frame.winfo_children()[2]
        self.active_list = tk.Listbox(self.list_frame, bg=self.sidebar_color, fg='black', highlightbackground="white")  # 将highlightbackground设为白色
        self.active_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        years = [str(year) for year in range(1992, 2021)]
        for year in years:
            self.active_list.insert(tk.END, year)

    def setup_content(self):
        self.content_frame = tk.Frame(self.root, bg=self.content_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.content_frame.pack_propagate(False)

        self.create_page_title()
        self.create_content_text()

    def create_page_title(self):
        self.page_title_label = tk.Label(
            self.content_frame, text="中国GDP可视化", font=("Arial", 20),
            height=3, bg=self.content_color, fg='black'
        )
        self.page_title_label.pack(side=tk.TOP, fill=tk.X)

    def create_content_text(self):
        self.content_text = tk.Text(
            self.content_frame, bg=self.content_color, fg='black',
            insertbackground='black'
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

def main():
    root = tk.Tk()
    style = ttk.Style(root)
    style.configure('Light.TButton', foreground='black', background='#F0F0F0', bordercolor='white')
    App(root)
    root.mainloop()

if __name__ == '__main__':
    main()
