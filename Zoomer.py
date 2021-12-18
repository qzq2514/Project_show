from tkinter import *
from PIL import Image, ImageTk
import tkinter.font as tkFont
import cv2

class Zoomer():
    def __init__(self, main_master, master, image, str_main):
        self.main_master = main_master
        self.font = tkFont.Font(family='Helvetica', size=20)
        self.tkObj = master
        self.tkObj.title("Zoomer")
        self.tkObj.resizable(width=False, height=False)
        self.tkObj.bind("<Z>", self.return_main)
        self.str_show = list(str_main.values())[0]
        # 图片显示区域
        h, w, c = image.shape
        self.ImgPanel = Canvas(self.tkObj, cursor='tcross')
        self.ImgPanel.config(width=w, height=h)
        self.ImgPanel.pack()
        self.imgPIL = ImageTk.PhotoImage(Image.fromarray(image))

        self.ImgPanel.create_image(0, 0, image=self.imgPIL, anchor=NW)
        self.ImgPanel.create_text(w//3, 30, text=self.str_show, fill="red", font=self.font)

    def return_main(self, event=None):
        self.main_master.delete_zoomer()