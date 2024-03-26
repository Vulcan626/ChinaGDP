import tkinter as tk
from tkinter import ttk
import pandas as pd
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns
import plotly as py
import plotly.io as pio
import plotly.graph_objs as go
import json

# 设置Matplotlib中文显示
plt.rcParams['font.sans-serif'] = ['Arial']
plt.rcParams['axes.unicode_minus'] = False

# 数据加载和预处理
# chinagdp_df
chinagdp_df = pd.read_csv('dataset/Chinas GDP in Province En.csv', encoding='utf-8')
chinagdp_df.rename({'Unnamed: 0': 'year', 'Guangxi,': 'Guangxi'}, axis=1, inplace=True)
# china_gdp_df2
chinagdp_df2 = chinagdp_df.melt(id_vars=['year'],
                                var_name=['province'],
                                value_name='gdp')
# regions_df
regions_df = pd.read_csv('dataset/china_regions.csv')
# 合并数据
regions_merge = chinagdp_df2.merge(regions_df, how='left')
regions_composition = regions_merge[['region', 'province']].drop_duplicates()

regions_composition.sort_values('region') \
    .reset_index() \
    .drop(columns='index')

regions_merge['gdp_total'] = regions_merge.groupby(['region', 'year']) \
    .gdp.transform('sum')

gdp_regions = regions_merge[['region', 'year', 'gdp_total']].drop_duplicates()

# 为了方便后续的绘图，对数据进行排序
chinagdp_df2 = chinagdp_df2[['province', 'year', 'gdp']] \
    .sort_values(['province', 'year']) \
    .reset_index(drop=True)

# 读取中国地图的GeoJSON文件
chinagdp_norm = chinagdp_df2.copy()
chinagdp_norm['percentage_per_year'] = 100 * chinagdp_norm.gdp / chinagdp_norm.groupby('year').gdp.transform('sum')

chinagdp_norm = chinagdp_norm.sort_values(['year', 'province'])

with open('dataset/china_modified.json') as file:
    china_json = json.load(file)


# 创建App类
class App:
    def __init__(self, root):
        # 初始化应用程序界面
        self.window = None
        self.page_title_label = None
        self.content_frame = None
        self.list_frame = None
        self.functions_frame = None
        self.sidebar_frame = None
        self.content_text = None
        self.root = root
        self.root.title("Chinese GDP Visualization")  # 设置窗口标题
        self.root.minsize(800, 600)  # 设置窗口最小大小
        self.root.configure(bg="white")  # 设置窗口背景颜色

        # 定义侧边栏和内容栏的颜色
        self.sidebar_color = "#F0F0F0"  # 侧边栏颜色
        self.content_color = "white"  # 内容栏颜色
        self.home_text = ("Welcome to the Chinese GDP Visualization App!\n\nThis app allows you to visualize the GDP "
                          "data of China.\n\nPlease select a function from the sidebar.\n\nCreated by Vulcan626 on "
                          "2024/3/25")  # 主页文本内容

        # 设置侧边栏和内容栏
        self.setup_sidebar()
        self.setup_content()

        self.active_button = None
        self.active_list = None

    def setup_sidebar(self):
        # 设置侧边栏
        self.sidebar_frame = tk.Frame(self.root, width=200, bg=self.sidebar_color)
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
        self.sidebar_frame.pack_propagate(False)

        # 创建功能按钮
        self.functions_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color)
        self.functions_frame.pack(fill=tk.X, pady=(0, 20))
        self.create_functions()

        # 创建用于显示列表的框架
        self.list_frame = tk.Frame(self.sidebar_frame, bg=self.sidebar_color, highlightbackground="white")
        self.list_frame.pack(fill=tk.BOTH, expand=True)

    def create_functions(self):
        # 创建功能按钮
        function_names = ["Clear", "Total GDP Trend", "Regional GDP Comparison", "Provincial GDP Trend",
                          "Provincial GDP Distribution"]  # 功能名称列表
        for idx, name in enumerate(function_names):
            button = ttk.Button(
                self.functions_frame, text=name, style='Light.TButton',
                command=lambda idx=idx: self.toggle_list(idx)
            )
            button.pack(fill=tk.X, padx=5, pady=5)

    def toggle_list(self, idx):
        # 切换功能列表
        if self.active_button and self.active_button == self.functions_frame.winfo_children()[idx]:
            return

        if self.active_list:
            self.active_list.destroy()

        if idx == 0:
            self.clear_plot()
        elif idx == 1:
            self.plot_total_gdp_trend()
        elif idx == 2:
            self.plot_region_gdp_comparison()
        elif idx == 3:
            self.create_provinces_list()
        elif idx == 4:
            self.create_years_list()
        else:
            self.active_button = None

    def setup_content(self):
        # 设置内容栏
        self.content_frame = tk.Frame(self.root, bg=self.content_color)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.content_frame.pack_propagate(False)

        # 设置页面标题标签
        self.page_title_label = tk.Label(
            self.content_frame, text="Chinese GDP Visualization", font=("Arial", 20),
            height=3, bg=self.content_color, fg='black'
        )
        self.page_title_label.pack(side=tk.TOP, fill=tk.X)

        # 创建内容文本框
        self.create_content_text()

    def create_content_text(self):
        # 创建内容文本框
        self.content_text = tk.Text(
            self.content_frame, bg=self.content_color, fg='black',
            insertbackground='black'
        )
        self.content_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.content_text.insert(tk.END, self.home_text)

    def show_figure(self, plt):
        # 在Tkinter中显示Matplotlib图形
        fig = plt.gcf()
        canvas = FigureCanvasTkAgg(fig, master=self.content_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill=tk.BOTH, expand=True)
        canvas.draw()

    def create_provinces_list(self):
        self.active_button = self.functions_frame.winfo_children()[3]
        self.active_list = tk.Listbox(self.list_frame, bg=self.sidebar_color, fg='black', highlightbackground="white")
        self.active_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 获取所有省份列表
        provinces = chinagdp_df2['province'].unique().tolist()
        provinces.sort()  # 按字母顺序排序

        # 添加 "All Province" 选项
        self.active_list.insert(tk.END, "All Province")

        # 将省份添加到列表中
        for province in provinces:
            self.active_list.insert(tk.END, province)

        # 绑定列表项点击事件
        self.active_list.bind('<<ListboxSelect>>', self.on_province_select)

    def create_years_list(self):
        self.active_button = self.functions_frame.winfo_children()[4]  # 获取第五个按钮
        self.active_list = tk.Listbox(self.list_frame, bg=self.sidebar_color, fg='black', highlightbackground="white")  # 创建列表框
        self.active_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        years = [str(year) for year in range(1992, 2021)]  # 创建年份列表
        for year in years:
            self.active_list.insert(tk.END, year)  # 将年份插入列表

        self.active_list.bind('<<ListboxSelect>>', self.on_year_select)  # 绑定列表项点击事件

    def clear_plot(self):
        # 清除先前的图表
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def on_province_select(self, event):
        # 获取选中的省份
        selected_province = self.active_list.get(self.active_list.curselection())

        # 绘制选中省份的GDP趋势图
        self.plot_province_gdp_trend(selected_province)

    def on_year_select(self, event):
        # 获取选中的年份
        selected_year = self.active_list.get(self.active_list.curselection())

        # 绘制选中年份的GDP分布图
        self.plot_province_gdp_distribution(selected_year)

    def plot_total_gdp_trend(self):
        # 清除先前的图表
        self.clear_plot()

        # 计算全国每年的GDP总和
        total_gdp_per_year = chinagdp_df.drop(columns='year').sum(axis=1)
        years = chinagdp_df['year']

        # 创建图表
        plt.figure(figsize=(15, 8))
        sns.lineplot(x=years, y=total_gdp_per_year)
        plt.title('Total GDP Trend in China')
        plt.xlabel('Year')
        plt.ylabel('Total GDP')

        # 将matplotlib图表显示在Tkinter中
        self.show_figure(plt)

    def plot_region_gdp_comparison(self):
        # 清除先前的图表
        self.clear_plot()

        # 创建新的图表
        plt.figure(figsize=(10, 8))
        sns.set_style('dark')
        sns.set_palette('bright')
        axbp = sns.boxplot(data=gdp_regions, x='region', y='gdp_total')
        axbp.set_title('Regional GDP Comparison')

        # 将matplotlib图表显示在Tkinter中
        self.show_figure(plt)

    def plot_province_gdp_trend(self, province):
        # 清除先前的图表
        self.clear_plot()

        # 如果选中的是 "All Province"，则绘制所有省份的趋势图
        if province == "All Province":
            # 创建图表
            plt.figure(figsize=(15, 8))
            sns.set_style('dark')
            sns.set_palette('bright')

            # 遍历所有省份，绘制每个省份的趋势图
            for province in chinagdp_df2['province'].unique():
                province_data = chinagdp_df2[chinagdp_df2['province'] == province]
                sns.lineplot(data=province_data, x='year', y='gdp', label=province)

            # 添加标题和标签
            plt.title('Provincial GDP Trend in China')
            plt.xlabel('Year')
            plt.ylabel('GDP')
            plt.legend(loc='upper left')

            # 将matplotlib图表显示在Tkinter中
            self.show_figure(plt)

        else:
            # 根据选定的省份绘制趋势图
            province_data = chinagdp_df2[chinagdp_df2['province'] == province]

            # 创建图表
            plt.figure(figsize=(10, 6))
            sns.set_style('dark')
            sns.lineplot(data=province_data, x='year', y='gdp')

            # 添加标题和标签
            plt.title(f'GDP Trend in {province}')
            plt.xlabel('Year')
            plt.ylabel('GDP')

            # 将matplotlib图表显示在Tkinter中
            self.show_figure(plt)

    def plot_province_gdp_distribution(self, year):
        # 清除先前的图表
        self.clear_plot()

        # 添加年份标题
        title_label = tk.Label(self.content_frame, text=f'Annual GDP in {year}', font=("Arial", 16), bg=self.content_color)
        title_label.pack(anchor=tk.CENTER, pady=(20, 0))

        # 创建一个 Label 来显示图片
        img_path = f'img/china_gdp_{year}.png'
        img = tk.PhotoImage(file=img_path)
        img_label = tk.Label(self.content_frame, image=img)
        img_label.image = img
        img_label.pack(anchor=tk.CENTER, padx=20, pady=20)




def main():
    # 主函数入口
    root = tk.Tk()
    style = ttk.Style(root)
    style.configure('Light.TButton', foreground='black', background='#F0F0F0', bordercolor='white')  # 设置按钮样式
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
