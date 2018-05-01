# coding=utf-8
"""
Author: Dylan
For my love, XYY
"""
import datetime
from FileDialog import *
import tkFileDialog

import core_functions


class MainPanel:
    def __init__(self):
        self.root = Tk()
        self.selected_folder = "./"
        self.yang_frame = Frame(self.root)
        self.select_folder_b = Button(self.yang_frame, text="选择文件夹", height=2, width=10, command=self.select_folder)
        self.yang_label = Label(self.yang_frame, text="-->")
        self.yang_sum_b = Button(self.yang_frame, text="杨氏模量求和", height=2, width=10, command=self.sum_all_yang_value)

        self.select_folder_b.pack(side=LEFT)
        self.yang_label.pack(side=LEFT)
        self.yang_sum_b.pack(side=LEFT)
        self.yang_frame.pack()
        self.root.title("圆圆计算器")
        self.center_window(self.root, 500, 400)
        self.root.mainloop()

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def select_folder(self):
        self.selected_folder = tkFileDialog.askdirectory()

    def sum_all_yang_value(self):
        """
        遍历所选文件夹下所有txt文件，计算杨氏模量的和, 并存储到csv文件中
        :return:
        """
        files = core_functions.get_files(self.selected_folder, ".txt")
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