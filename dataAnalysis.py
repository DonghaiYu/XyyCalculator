# coding=utf-8
"""
Author: Dylan
For my love, XYY
"""
import datetime
from FileDialog import *
import tkFileDialog

import core_functions


class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

    def write(self,string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class MainPanel:
    def __init__(self):
        self.root = Tk()
        self.yang_data_folder = "./"
        self.cell_label_data_folder = ""

        self.split_line1 = Label(self.root, text="=========杨氏模量求和=========")
        self.split_line1.pack()

        # 杨氏模量求和模块
        self.yang_frame = Frame(self.root)
        self.yang_folder_b = Button(self.yang_frame, text="选择文件夹", height=2, width=10, command=self.yang_folder)
        self.yang_label = Label(self.yang_frame, text="-->")
        self.yang_sum_b = Button(self.yang_frame, text="杨氏模量求和", height=2, width=10, command=self.sum_all_yang_value)

        self.yang_folder_b.pack(side=LEFT)
        self.yang_label.pack(side=LEFT)
        self.yang_sum_b.pack(side=LEFT)
        self.yang_frame.pack()

        self.split_line1 = Label(self.root, text="========cell label analysis==========")
        self.split_line1.pack()

        # 细胞标签分析模块
        self.cell_label_frame = Frame(self.root)
        self.cell_label_folder_b = Button(self.cell_label_frame, text="choose data folder", height=2, width=15, command=self.cell_label_folder)
        self.hour_label = Label(self.cell_label_frame, text="--> hours:")
        self.hours = Entry(self.cell_label_frame, width=10)
        self.hours.insert(END, '0,24')
        self.hour_suffix_label = Label(self.cell_label_frame, text=" file suffix:")
        self.hours_suffix = Entry(self.cell_label_frame, width=10)
        self.hours_suffix.insert(END, 'h cell No')

        self.cell_analysis_b = Button(self.cell_label_frame, text="go", height=2, width=10, command=self.cell_analysis)

        self.cell_label_folder_b.pack(side=LEFT)
        self.hour_label.pack(side=LEFT)
        self.hours.pack(side=LEFT)
        self.hour_suffix_label.pack(side=LEFT)
        self.hours_suffix.pack(side=LEFT)
        self.cell_analysis_b.pack(side=LEFT)
        self.cell_label_frame.pack()

        # 日志区
        self.text_box = Text(self.root, wrap='word', height=15, width=100)
        # self.text_box.grid(column=0, row=0, columnspan=2, sticky='NSWE', padx=5, pady=5)
        self.text_box.pack()
        sys.stdout = StdoutRedirector(self.text_box)

        self.root.title("圆圆计算器")
        self.center_window(self.root, 700, 500)
        self.root.mainloop()

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def yang_folder(self):
        self.yang_data_folder = tkFileDialog.askdirectory()

    def cell_label_folder(self):
        self.cell_label_data_folder = tkFileDialog.askdirectory()
        print("your selected folder: {}".format(self.cell_label_data_folder))

    def cell_analysis(self):
        hours = self.hours.get()
        hours = hours.split(",")
        hours = [int(x) for x in hours]
        area_suffix = self.hours_suffix.get()
        area_files = ["{}{}.csv".format(h, area_suffix) for h in hours]
        area_f_set = set(area_files)
        find_area_f_set = set()
        interval_folders = []

        if not os.path.isdir(self.cell_label_data_folder):
            print("error! unknown data path: {}".format(self.cell_label_data_folder))
            return
        for f in os.listdir(self.cell_label_data_folder):
            if f in area_f_set:
                find_area_f_set.add(f)
            abs_path = self.cell_label_data_folder + "/" + f
            if os.path.isdir(abs_path):
                interval_folders.append(abs_path)

        if len(find_area_f_set) == len(area_f_set):
            print("find all the area files, success. area files:")
            print(area_files)
        else:
            print("error! can not find {}".format(area_f_set - find_area_f_set))
            return

        print("label2label map data folders:")
        print(interval_folders)

        core_functions.label_analysis(self.cell_label_data_folder, area_suffix, interval_folders, hours)

    def sum_all_yang_value(self):
        """
        遍历所选文件夹下所有txt文件，计算杨氏模量的和, 并存储到csv文件中
        :return:
        """
        files = core_functions.get_files(self.yang_data_folder, ".txt")
        result_lst = []
        for file_item in files:
            file_path, file_name = os.path.split(file_item)
            try:
                file_sort_index = int(file_name[:-4])
            except Exception as e:
                file_sort_index = 0
            sum_result, sum_line_num = core_functions.sum_data(file_item)
            result_lst.append([file_path, file_sort_index, file_name, sum_result, sum_line_num])

        result_lst.sort(key=lambda x: (x[0], x[1]))

        current_time = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        with open("./data/Young_modulus_sum_{}.csv".format(current_time), "w") as result_file:
            result_file.writelines(",".join(["folder path", "file index", "file name", "sum result", "file line num"]) + "\n")
            for item in result_lst:
                print(item)
                items = [str(x) for x in item]
                result_file.writelines(",".join(items) + "\n")


def main():
    main_panel = MainPanel()


if __name__ == "__main__":
    main()
