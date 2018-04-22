# coding=utf-8
import os
import sys
from Tkinter import *
from FileDialog import *
import core_functions


class MainPanel:
    def __init__(self):
        self.root = Tk()
        self.selected_folder = "."
        self.select_folder_b = Button(self.root, text="杨氏模量求和", command=self.select_folder)
        self.select_folder_b.pack()
        self.root.mainloop()

    def select_folder(self):
        fd = LoadFileDialog(self.root)
        self.selected_folder = fd.go()
        core_functions.get_files(self.selected_folder, ".txt")

def main():
    main_panel = MainPanel()


if __name__ == "__main__":
    main()