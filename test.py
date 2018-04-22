# coding=utf-8
"""
from Tkinter import *
from FileDialog import *
 
root = Tk()
 
fd = LoadFileDialog(root) # 创建打开文件对话框
filename = fd.go()
print(filename)
"""
from Tkinter import *
from FileDialog import *


class StdoutRedirector(object):
    def __init__(self,text_widget):
        self.text_space = text_widget

    def write(self,string):
        self.text_space.insert('end', string)
        self.text_space.see('end')


class CoreGUI(object):
    def __init__(self,parent):
        self.parent = parent
        self.InitUI()
        button = Button(self.parent, text="Start", command=self.main)
        button.grid(column=0, row=1, columnspan=2)

    def main(self):
        print('whatever')

    def InitUI(self):
        self.text_box = Text(self.parent, wrap='word', height = 11, width=50)
        self.text_box.grid(column=0, row=0, columnspan = 2, sticky='NSWE', padx=5, pady=5)
        sys.stdout = StdoutRedirector(self.text_box)


root = Tk()
gui = CoreGUI(root)
root.mainloop()
