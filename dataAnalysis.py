# coding=utf-8
import os
import sys
from Tkinter import *
from FileDialog import *
import tkFileDialog

import core_functions


class MainPanel:
    def __init__(self):
        self.root = Tk()
        self.selected_folder = "."
        self.select_folder_b = Button(self.root, text="杨氏模量求和", command=self.select_folder)
        self.select_folder_b.pack()
        self.root.mainloop()

    def select_folder(self):
		self.selected_folder = tkFileDialog.askdirectory()
		print(self.selected_folder)
        files = core_functions.get_files(self.selected_folder,".txt")

def main():
    main_panel = MainPanel()


if __name__ == "__main__":
    main()