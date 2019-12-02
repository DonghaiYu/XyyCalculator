# coding=utf-8
"""
Author: Dylan
For my love, XYY
"""
import datetime
import logging
from tkinter.filedialog import *
from tkinter import filedialog
import cv2

import core_functions
import lineDetector

YANG_FOLDER = "yang_folder"
CELL_LABEL_FOLDER = "cell_label_folder"
HOURS_VAR = "hours_var"
SUFFIX_VAR = "suffix_var"
LINE_IMG = "line_img"
ZOOM_VAR = "zoom_var"
REC_VAR = "rec_var"

TASK1_INTRODUCTION = """
    task1: sum Young modulus
"""

TASK2_INTRODUCTION = """
    task2: time-series cell label analysis
"""

TASK3_INTRODUCTION = """
    task3: line detector
"""


class TextHandler(logging.Handler):
    """This class allows you to log to a Tkinter Text or ScrolledText widget"""
    def __init__(self, text):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.text = text

    def emit(self, record):
        msg = self.format(record)

        def append():
            self.text.insert(END, msg + '\n')
            # Autoscroll to the bottom
            self.text.see(END)
        # This is necessary because we can't modify the Text from other threads
        self.text.after(0, append)


class StdoutRedirector(object):
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class MainPanel:
    def __init__(self):
        self.root = Tk()
        self.line_detector_img = ''
        self.input_data = {}

        self.head_frame = Frame(self.root)
        t1 = Button(self.head_frame, text="task1", height=2, width=15, command=self.task1_frame)
        t2 = Button(self.head_frame, text="task2", height=2, width=15, command=self.task2_frame)
        t3 = Button(self.head_frame, text="task3", height=2, width=15, command=self.task3_frame)
        t1.pack(side=LEFT)
        t2.pack(side=LEFT)
        t3.pack(side=LEFT)
        self.head_frame.pack()
        self.detail_frame = Frame(self.root)
        self.detail_frame.pack()
        self.log_frame = Frame(self.root)
        self.logger = None
        self.text_handler = None
        self.reload_log_frame()

        self.root.title("YyX's calculator")
        self.center_window(self.root, 800, 600)
        # self.root.mainloop()

    def reload_log_frame(self):
        if self.log_frame is not None:
            #self.log_frame.pack_forget()
            self.log_frame.destroy()
        self.log_frame = Frame(self.root)

        text_box = Text(self.log_frame, wrap='word', height=20, width=100)
        clean_b = Button(self.log_frame, text='clear log text', height=2, width=15,
                         command=lambda: text_box.delete('1.0', 'end'))
        logFormatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")
        self.file_handler = logging.FileHandler("data/log.log")
        self.text_handler = TextHandler(text_box)
        self.text_handler.setFormatter(logFormatter)
        self.file_handler.setFormatter(logFormatter)
        self.logger = logging.getLogger()
        self.logger.handlers = []
        self.logger.addHandler(self.text_handler)
        self.logger.addHandler(self.file_handler)
        self.logger.setLevel(logging.DEBUG)

        text_box.pack()
        clean_b.pack()
        # sys.stdout = StdoutRedirector(text_box)
        self.log_frame.pack()

    def task1_frame(self):
        if self.detail_frame is not None:
            self.detail_frame.destroy()
        # 杨氏模量求和模块
        self.detail_frame = Frame(self.root)
        yang_folder_b = Button(self.detail_frame, text="choose folder", height=2, width=10,
                               command=lambda: self.askdirectory(YANG_FOLDER))
        yang_sum_b = Button(self.detail_frame, text="run", height=2, width=5, fg='red',
                            command=self.sum_all_yang_value)

        yang_folder_b.pack(side=LEFT)
        yang_sum_b.pack(side=LEFT)
        self.detail_frame.pack(fill=X)
        self.reload_log_frame()
        logging.info(TASK1_INTRODUCTION)

    def task2_frame(self):
        if self.detail_frame is not None:
            self.detail_frame.destroy()
        hours_var = StringVar()
        suffix_var = StringVar()

        # 细胞标签分析模块
        self.detail_frame = Frame(self.root)
        cell_label_folder_b = Button(self.detail_frame, text="choose folder", height=2, width=15,
                                     command=lambda: self.askdirectory(CELL_LABEL_FOLDER))
        hour_label = Label(self.detail_frame, text=" hours:")
        hours = Entry(self.detail_frame, width=10, textvariable=hours_var)
        hours.insert(END, '0,24')
        hour_suffix_label = Label(self.detail_frame, text=" file suffix:")
        hours_suffix = Entry(self.detail_frame, width=10, textvariable=suffix_var)
        hours_suffix.insert(END, 'h cell No')

        cell_analysis_b = Button(self.detail_frame, text="run", height=2, width=10, fg='red',
                                 command=self.cell_analysis)
        self.input_data[HOURS_VAR] = hours_var
        self.input_data[SUFFIX_VAR] = suffix_var

        cell_label_folder_b.pack(side=LEFT)
        hour_label.pack(side=LEFT)
        hours.pack(side=LEFT)
        hour_suffix_label.pack(side=LEFT)
        hours_suffix.pack(side=LEFT)
        cell_analysis_b.pack(side=LEFT)
        self.detail_frame.pack(fill=X)
        self.reload_log_frame()
        logging.info(TASK2_INTRODUCTION)

    def task3_frame(self):
        if self.detail_frame is not None:
            self.detail_frame.destroy()

        # 直线检测模块
        self.detail_frame = Frame(self.root)
        line_detector_img_b = Button(self.detail_frame, text="choose img", height=2, width=15,
                                     command=lambda: self.ask_file_name(LINE_IMG))

        zoom_var = StringVar()
        rec_var = StringVar()

        zoom_label = Label(self.detail_frame, text=" zoom width(px):")
        zoom_w_e = Entry(self.detail_frame, width=10, textvariable=zoom_var)
        zoom_w_e.insert(END, '800')
        rec_label = Label(self.detail_frame, text=" rectangle areas(1:yes;0:no):")
        rec_e = Entry(self.detail_frame, width=10, textvariable=rec_var)
        rec_e.insert(END, '1')
        line_detect_b = Button(self.detail_frame, text="run", height=2, width=10, fg='red',
                               command=self.line_detect)
        self.input_data[ZOOM_VAR] = zoom_var
        self.input_data[REC_VAR] = rec_var

        line_detector_img_b.pack(side=LEFT)
        zoom_label.pack(side=LEFT)
        zoom_w_e.pack(side=LEFT)
        rec_label.pack(side=LEFT)
        rec_e.pack(side=LEFT)
        line_detect_b.pack(side=LEFT)
        self.detail_frame.pack(fill=X)
        self.reload_log_frame()
        logging.info(TASK3_INTRODUCTION)

    def line_detect(self):
        img_path = self.input_data.get(LINE_IMG, None)
        if img_path is None or img_path == '':
            logging.error("please choose detect img first!")
            return
        zoom_w = int(self.input_data.get(ZOOM_VAR).get())
        rec = int(self.input_data[REC_VAR].get())
        rec = True if rec == 1 else False
        result_img, result_lines = lineDetector.do_detect(img_path, zoom_w, rec)
        f = filedialog.asksaveasfile(mode='w', defaultextension=".csv")
        logging.info("save line angle data in: " + f.name)
        if f is None:  # asksaveasfile return `None` if dialog closed with "cancel".
            return
        result_img_path = f.name.split(".")[0] + ".png"
        logging.info("save line detector img in: " + result_img_path)
        for idx, ang in result_lines:
            f.writelines(",".join([str(idx), str(ang)]) + "\n")
        f.close()
        cv2.imwrite(result_img_path, result_img)

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(size)

    def askdirectory(self, param_name):
        self.input_data[param_name] = filedialog.askdirectory()
        logging.info("your selected folder: {}".format(self.input_data[param_name]))

    def ask_file_name(self, param_name):
        self.input_data[param_name] = filedialog.askopenfilename()
        logging.info("your selected file is: {}".format(self.input_data[param_name]))

    def sum_all_yang_value(self):
        """
        遍历所选文件夹下所有txt文件，计算杨氏模量的和, 并存储到csv文件中
        :return:
        """
        folder_path = self.input_data.get(YANG_FOLDER, None)
        if folder_path is None or folder_path == '':
            logging.error("please choose folder first!")
            return
        files = core_functions.get_files(folder_path, ".txt")
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
                logging.info(item)
                items = [str(x) for x in item]
                result_file.writelines(",".join(items) + "\n")

    def cell_analysis(self):
        hours = self.input_data[HOURS_VAR].get()
        hours = hours.split(",")
        hours = [int(x) for x in hours]
        area_suffix = self.input_data[SUFFIX_VAR].get()
        area_files = ["{}{}.csv".format(h, area_suffix) for h in hours]
        area_f_set = set(area_files)
        find_area_f_set = set()
        interval_folders = []

        data_folder = self.input_data.get(CELL_LABEL_FOLDER, None)
        if data_folder is None or data_folder == '':
            logging.error("please choose folder first!")
            return

        if not os.path.isdir(data_folder):
            logging.error("unknown data path: {}".format(data_folder))
            return
        for f in os.listdir(data_folder):
            if f in area_f_set:
                find_area_f_set.add(f)
            abs_path = data_folder + "/" + f
            if os.path.isdir(abs_path):
                interval_folders.append(abs_path)

        if len(find_area_f_set) == len(area_f_set):
            logging.info("find all the area files, success. area files:")
            logging.info(area_files)
        else:
            logging.error("error! can not find {}".format(area_f_set - find_area_f_set))
            return

        logging.info("label2label map data folders:")
        logging.info(interval_folders)

        core_functions.label_analysis(data_folder, area_suffix, interval_folders, hours)


def main():
    main_panel = MainPanel()
    main_panel.root.mainloop()


if __name__ == "__main__":
    main()
