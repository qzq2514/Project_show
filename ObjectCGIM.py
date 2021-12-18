import os
import copy
import cv2
from tkinter.filedialog import *
from Rect import Rect
import json

class ObjectCGIM:
    def __init__(self, obj_id, obj_dict):
        # rect_main:代表目标的包围框,该属性必不可少
        self.obj_id = obj_id
        self.rect_main = None
        self.str_main = {}
        self.str_attrs = {}      # 其他可能的字符串属性集合
        self.rect_attrs = []     # 其他可能的包围框
        self.rect_list_attrs = {}
        self.draw_ids = {}      # 后面在tkinter上画矩形框时的全部id
        self.vars = {}          # 后面在tkinter上选择是否画对应的矩形框

        self.dict2obj(obj_dict)

    def dict2obj(self, obj_dict):
        for key, value in obj_dict.items():
            if key.endswith("_str") or key.endswith("_strmain"):
                self.str_attrs[key[:key.find("_")]] = value
                if key.endswith("_strmain"):
                    self.str_main[key[:key.find("_")]] = value
                    self.draw_ids[key[:key.find("_")]] = -1
            elif key.endswith("_bbmain"):
                cur_key = key[:key.find("_")]
                xmin, ymin, xmax, ymax = [float(v) for v in value.split(" ")]
                self.rect_main = Rect(cur_key, xmin, ymin, xmax, ymax)
                self.draw_ids[cur_key] = -1

            elif key.endswith("_bb"):
                cur_key = key[:key.find("_")]
                xmin, ymin, xmax, ymax = [float(v) for v in value.split(" ")]
                self.rect_attrs.append(Rect(cur_key, xmin, ymin, xmax, ymax))
                self.draw_ids[cur_key] = -1

            elif key.endswith("_bblist"):
                cur_rects=[]
                cur_key = key[:key.find("_")]
                for var in value:
                    xmin, ymin, xmax, ymax = [float(v) for v in var.split(" ")]
                    cur_rects.append(Rect("", xmin, ymin, xmax, ymax))
                self.rect_list_attrs[cur_key] = cur_rects
                self.draw_ids[cur_key] = [-1]*len(cur_rects)


if __name__ == '__main__':
    image = cv2.imread("test_data/pics/multi.png")
    h, w, c = image.shape
    with open("test_data/lpr_res.json", "r") as fr:
        result_dict = json.load(fr)
        for id, element in enumerate(result_dict["multi.png"]):
            obj = ObjectCGIM(id, element)

            print(obj.draw_ids)
            # 画rect_attrs中的框
            # print(obj.rect_attrs)
            for rect in obj.rect_attrs:
                # print(rect.name)
                xmin, ymin, xmax, ymax = int(rect.xmin * w), int(rect.ymin * h), int(rect.xmax * w), int(rect.ymax * h)
                cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255))

            # 画rect_main
            # rect = obj.rect_main
            # xmin, ymin, xmax, ymax = int(rect.xmin * w), int(rect.ymin * h), int(rect.xmax * w), int(rect.ymax * h)
            # cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255))

            # 画所有rect_list_attrs中的框
            # for rects in obj.rect_list_attrs[0].values():
            #     for rect in rects:
            #         xmin, ymin, xmax, ymax = int(rect.xmin * w), int(rect.ymin * h), int(rect.xmax * w), int(rect.ymax * h)
            #         cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (0, 0, 255))
    cv2.imshow("image", image)
    cv2.waitKey()
