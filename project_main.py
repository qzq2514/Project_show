import cv2
import time
import multiprocessing
import tkinter.font as tkFont
from ObjectCGIM import ObjectCGIM
from scipy import misc
from tkinter import ttk
from Utils import glob_images
from tkinter.filedialog import *
from PIL import Image, ImageTk
from Zoomer import Zoomer

image_width, image_height = 1000, 600
list_image_factor = 4
list_nums = 5

class USALPR():
    def __init__(self, master):
        self.tk_obj = master
        self.tk_obj.title("USALPR")
        self.tk_obj['width'] = 1880
        self.tk_obj['height'] = 100
        self.font = tkFont.Font(family='Helvetica', size=24)  # 图中显示文字大小
        self.tk_obj.resizable(width=False, height=False)

        self.empty_image = misc.imread("empty.png")
        self.tk_obj.bind("D", self.change_image(1))
        self.tk_obj.bind("A", self.change_image(-1))
        # self.tk_obj.bind("<Return>", self.load_dir)
        # self.tk_obj.bind("<space>", self.start_pause_video)
        ttk.Style().configure('rec_panel.TLabel', font=('Helvetica', 20), foreground="black")
        ttk.Style().configure('videoBig.TButton', font=('Helvetica', 30), foreground="black")
        ttk.Style().configure('videoSmall.TButton', font=('Helvetica', 24), foreground="black")

        # 先初始化一些非tk控件的参数
        self.init_tool_attr()

        # 上方区域:包括主图片显示和识别信息显示
        self.top_frame = Frame(self.tk_obj)
        self.top_frame.pack(side=TOP)

        # 左上区域:界面头部、主图片显示区、图片跳转控制区
        left_top_frame = Frame(self.top_frame)
        left_top_frame.pack(side=LEFT)

        # 界面头部:运行时间显示、路径输入框、加载按钮...
        head_frame = Frame(left_top_frame)
        head_frame.pack(side=TOP)

        ttk.Label(head_frame, text="所用时间:").pack(side=LEFT)
        self.time_label = ttk.Label(head_frame, text="00.00s:")
        self.time_label.pack(side=LEFT, padx=5)

        dir_lab = ttk.Label(head_frame, text="加载文件夹:")
        dir_lab.pack(side=LEFT)

        self.dir_textbox = ttk.Entry(head_frame, width=20)
        self.dir_textbox.pack(side=LEFT, padx=10)

        load_mbtn = ttk.Menubutton(head_frame, text="加载")
        load_mbtn.pack(side=LEFT, padx=10)

        load_menu = Menu(load_mbtn, tearoff=False)
        load_menu.add_command(label="加载图片集", command=self.load_pics)
        load_menu.add_command(label="加载视频", command=self.load_video)
        # filemenu.add_separator()     # 添加分隔符(暂时用不到)
        load_mbtn.config(menu=load_menu)

        # 主图片显示区域
        image_frame = Frame(left_top_frame)
        image_frame.pack(side=TOP)

        self.cur_image = self.empty_image.copy()
        self.image_PIL = ImageTk.PhotoImage(Image.fromarray(self.cur_image).resize((image_width, image_height)))

        self.image_canv = Canvas(image_frame, cursor='tcross')
        self.image_canv.pack(side=TOP)
        self.image_canv.config(height=image_height, width=image_width)
        self.image_canv.create_image(0, 0, image=self.image_PIL, anchor=NW)  # image参数必须是全局变量(如这里设置成类的对象属性)
        self.image_canv.bind("<Motion>", self.mouseMove)
        self.image_canv.bind("<Button-1>", self.mouseClick)

        # 图片跳转的控制面板
        control_frame = Frame(left_top_frame)
        control_frame.pack(side=TOP)
        first_btn = ttk.Button(control_frame, text="<<", command=self.change_image(0, "goto"))
        first_btn.pack(side=LEFT, padx=10)
        pre_btn = ttk.Button(control_frame, text="上一张", command=self.change_image(-1))
        pre_btn.pack(side=LEFT, padx=10)
        next_btn = ttk.Button(control_frame, text="下一张", command=self.change_image(1))
        next_btn.pack(side=LEFT, padx=10)
        self.last_btn = ttk.Button(control_frame, text=">>")
        self.last_btn.pack(side=LEFT, padx=10)
        self.num_label = ttk.Label(control_frame, text="0/0")
        self.num_label.pack(side=LEFT, padx=10)
        goto_label = ttk.Label(control_frame, text="转到:")
        goto_label.pack(side=LEFT, padx=5)
        self.goto_entry = ttk.Entry(control_frame, width=5)
        self.goto_entry.pack(side=LEFT, padx=5)
        goto_btn = ttk.Button(control_frame, text="跳转", command=self.goto)
        goto_btn.pack(side=LEFT, padx=5)

        # 右上区域: 识别显示显示区域、视频控制区
        right_top_frame = Frame(self.top_frame)
        right_top_frame.pack(side=LEFT)

        # 识别信息的显示区域
        self.info_panel = Frame(right_top_frame)
        self.info_panel.pack(side=TOP)
        self.create_engine_comb()
        self.create_info_show_panel()

        # 视频控制区、输入数据是视频时的可用的一些选项，包括暂停/开始，设置读取帧率，
        self.video_panel = Frame(right_top_frame)
        self.creat_video_panel(self.video_panel)
        self.video_panel.pack(side=LEFT, pady=40)

        # 图片列表区域
        list_frame = Frame(self.tk_obj)
        list_frame.pack(side=BOTTOM)
        self.create_image_list(list_frame)
        # self.load_dir()

    def create_engine_comb(self):
        self.engine_comb = ttk.Combobox(self.info_panel, width=30)
        self.engine_comb.pack(side=TOP, pady=20)
        self.engine_modules = {}
        for file_name in os.listdir("."):
            if file_name.startswith("engine_"):
                module_name = os.path.splitext(file_name)[0]
                self.engine_modules[module_name] = __import__(module_name)

        self.engine_comb["value"] = ["None"] + list(self.engine_modules.keys())
        self.engine_comb.current(0)

    # 初始化，清空所有信息，恢复到一开始刚启动程序的那一刻
    def init_tool_attr(self):
        self.dir_path = None
        self.obj_list = []  # 当前图片的检测对象集合
        self.all_image_paths = []
        self.images_number = 0
        self.cur_image_id = -1  # 显示图片集中的第几章图片, 有效下标从0开始
        self.obj_id = 0  # 显示当前图片中的第几个检测对象
        self.max_str_attr_num = 4
        self.max_rect_attr_num = 4
        self.list_images = [self.empty_image] * list_nums
        self.module_name = "None" if not "engine_comb" in self.__dict__.keys() else self.engine_comb.get()
        self.pause = False    # 用于决定视频的播放/暂停(默认直接播放)
        self.video_cap = None
        self.interval_time = 0  # 视频/图片自动播放间隔(ms为单位)
        if "video_process" in self.__dict__.keys() and \
            self.__dict__["video_process"] is not None and self.__dict__["video_process"].is_alive:
            # print("video_process.terminate()")   # 问题1:进程无法被消除(输入视频运行后再转为图片集, video_func还是会一直运行)
            self.video_process.terminate()
            self.video_process.join()
        self.video_process = None
        self.zoomer = None

    # 初始化界面上tk控件，比如删除所有图像显示、清空label等
    def init_tool(self):
        # 1.先初始化一些属性信息
        self.init_tool_attr()

        # 2.初始化主图片显示区
        self.image_canv.delete(ALL)
        self.cur_image = self.empty_image.copy()
        self.image_PIL = ImageTk.PhotoImage(Image.fromarray(self.cur_image).resize((image_width, image_height)))
        self.image_canv.create_image(0, 0, image=self.image_PIL, anchor=NW)  # image参数必须是全局变量(如这里设置成类的对象属性)

        # 3.初始化图片列表
        # 经过调用init_tool_attr函数后，self.cur_image_id和self.all_image_paths都已经初始化了，直接可以update_image_list
        self.update_image_list()

        # 4.默认隐藏视频控制区
        # if "video_panel" in self.__dict__.keys():
        #     self.video_panel.pack_forget()

        # 5.初始化信息展示区label显示内容
        for str_attr_id in range(self.max_str_attr_num):
            self.rec_str_pair[str_attr_id][0].config(text="属性{}".format(str_attr_id))
            self.rec_str_pair[str_attr_id][1].config(text="xxx")

        # 5.初始化信息展示区checkbutton内容
        for rect_id in range(self.max_rect_attr_num):
            self.rec_rect_pair[rect_id][0].config(text="属性{}".format(rect_id))
            temp_var = IntVar(); temp_var.set(0)
            self.rec_rect_pair[rect_id][1].config(var=temp_var)
            # self.rec_rect_pair[rect_id][1].config(text)

        # 6.初始化图片id的label
        self.num_label.config(text="0/0")

    def change_speed(self, num):
        def change_speed_core(event=None):
            # 改变视频播放的时间间隔
            if self.interval_time+num < 0:
                return
            self.interval_time += num
            self.speed_lab.config(text="播放间隔: {} ms".format(self.interval_time))
            print("播放间隔: {} ms".format(self.interval_time))
        return change_speed_core

    def start_pause_video(self, event=None):
        if self.cur_image_id == self.images_number-1:  #已经是视频最后一帧,本来就是暂停的了,这时候暂停/开始键按也没用,因为都是暂停
            self.pause = True
        else:
            self.pause = not self.pause
        self.video_process.run()

    def creat_video_panel(self, panel):
        pause_video_btn = ttk.Button(panel, text="开始/暂停", style='videoBig.TButton', command=self.start_pause_video)
        pause_video_btn.pack(side=TOP, padx=10)

        self.speed_lab = ttk.Label(panel, text="播放间隔: {} ms".format(self.interval_time), style='rec_panel.TLabel')
        self.speed_lab.pack(side=LEFT, pady=38)    # 要不要添加倍速，再说吧

        slowdown_btn = ttk.Button(panel, text="减速", style='videoSmall.TButton', command=self.change_speed(50))
        slowdown_btn.pack(side=TOP, padx=10, pady=12)

        accelerate_btn = ttk.Button(panel, text="加速", style='videoSmall.TButton', command=self.change_speed(-50))
        accelerate_btn.pack(side=TOP, padx=10)

    def goto(self, event=None):
        try:
            number = int(self.goto_entry.get())
        except:
            # messagebox.showinfo("Waring", "Please input correct number!")
            return
        # number下标从1开始
        if number <1 or number > self.images_number:
            return

        self.cur_image_id = number-1
        self.update_image_panel()

    def change_image(self, num, type="nogoto"):
        def change_core(event=None):
            if type == "goto":    # 到达指定的图片
                if num >= 0 and num < self.images_number:
                    self.cur_image_id = num
                print("{}:{}".format(self.cur_image_id, self.pause))
            else:                 # 上一张下一张
                res_id = self.cur_image_id + num
                if res_id >= self.images_number or res_id < 0:
                    return
                self.cur_image_id = res_id
            self.update_image_panel()
        return change_core

    def video_func(self):
        try:
            while self.cur_image_id + 1 < self.images_number:
                time.sleep(self.interval_time/1000)
                if not self.pause:
                    self.cur_image_id += 1
                    self.update_image_panel()
                self.tk_obj.update_idletasks()  # 最重要的更新是靠这两句来实现
                self.tk_obj.update()
        except:
            print("An negligible exception occurred in the video_func()!")

    def load_core(self):
        self.cur_image_id = 0
        self.pause = False
        self.last_btn.config(command=self.change_image(self.images_number - 1, "goto"))  # 加载了所有图片后，才能知道最后一页的id
        self.video_process = multiprocessing.Process(target=self.video_func)
        self.video_process.start()
        self.video_process.run()

        # 根据当前id显示新图片,进行新图片的识别获取识别结果并更新识别面板和图片列表
        try:
            self.update_image_panel()
        except:
            print("An negligible exception occurred in update_image_panel()~")

    def load_video(self):
        self.init_tool()
        engine_name = self.engine_comb.get()
        if engine_name == "None":
            print("请先选择项目引擎!")
            return
        self.dir_path = self.dir_textbox.get().strip(' ')  # test_data/video/traffic.mp4

        ext = os.path.splitext(self.dir_path)[1]

        if ext not in [".mp4", ".avi", ".mov"]:     # 输入视频
            print("请输入正确格式的视频文件")
            return

        print("成功加载视频{}......".format(self.dir_path))
        self.video_panel.pack(side=LEFT, pady=40)

        # 设置视频的一些参数
        self.video_cap = cv2.VideoCapture(self.dir_path)
        self.images_number = int(self.video_cap.get(7))
        print("number:", self.images_number)

        self.load_core()

    def load_pics(self, event=None):
        self.init_tool()
        engine_name = self.engine_comb.get()
        if engine_name == "None":
            print("请先选择项目引擎!")
            return
        self.dir_path = self.dir_textbox.get().strip(' ')  #  test_data/pics

        if not os.path.exists(self.dir_path):
            print("文件夹不存在!!!")
            return

        self.all_image_paths = glob_images(self.dir_path)
        self.images_number = len(self.all_image_paths)

        if self.images_number == 0:
            print("该文件夹下没有图片!!")
            return
        self.load_core()

    def get_min_area_obj(self, position):
        x, y = position
        res_obj = None
        min_area = 1.0
        for obj in self.obj_list:
            rect = obj.rect_main
            xmin, ymin, xmax, ymax = rect.xmin, rect.ymin, rect.xmax, rect.ymax

            if x >= xmin and x <= xmax and y >= ymin and y <= ymax and rect.area < min_area:
                min_area = rect.area
                res_obj = obj
        return res_obj

    def delete_zoomer(self):
        if self.zoomer is not None:
            self.zoomer.tkObj.destroy()

    def mouseClick(self, event=None):
        x, y = event.x / image_width, event.y / image_height
        # print("{}:{}".format(event.x, event.y))
        res_obj = self.get_min_area_obj((x, y))
        if res_obj is None:
            return

        h, w, c = self.cur_image.shape
        rect = res_obj.rect_main
        xmin, xmax = int(rect.xmin * w),  int(rect.xmax * w)
        ymin, ymax = int(rect.ymin * h), int(rect.ymax * h)
        # self.cur_image是原始msic读取的图像
        zoom_image = self.cur_image[ymin:ymax, xmin:xmax]
        zoom_image = cv2.resize(zoom_image, (0, 0), fx=3, fy=3)
        zoomRoot = Toplevel()
        self.pause=True
        self.zoomer = Zoomer(self, zoomRoot, zoom_image, res_obj.str_main)
        zoomRoot.mainloop()

    def mouseMove(self, event=None):
        x, y = event.x/image_width, event.y/image_height
        res_obj = self.get_min_area_obj((x, y))

        if res_obj is not None:
            self.update_info_panel(res_obj)

    # 根据当前图片识别结果中的某个object
    def create_info_show_panel(self):

        # for widget in self.info_panel.winfo_children():
        #     widget.destroy()
        # self.info_panel.pack_forget()

        # 创建一些label显示车牌识别结果
        self.rec_str_pair = []
        for id in range(self.max_str_attr_num):
            self.rec_str_pair.append(self.create_rec_label(self.info_panel, key="属性{}".format(id), value="xxx"))

        self.rec_rect_pair = []
        for id in range(self.max_rect_attr_num):
            self.rec_rect_pair.append(self.create_rec_checkbutton(self.info_panel, key="属性{}".format(id)))

    def create_rec_label(self, rec_res_panel, key, value):
        temp_panel = Frame(rec_res_panel)
        temp_panel.pack(side=TOP, pady=5)
        if len(key) != 0:
            key_label = ttk.Label(temp_panel, text="{}:".format(key), style="rec_panel.TLabel", width=15)
            key_label.pack(side=LEFT, padx=5)
        value_label = ttk.Label(temp_panel, text=value, style="rec_panel.TLabel", width=15)
        value_label.pack(side=LEFT)
        return (key_label, value_label) if len(key) != 0 else value_label

    def create_rec_checkbutton(self, rec_res_panel, key):
        temp_panel = Frame(rec_res_panel)
        temp_panel.pack(side=TOP, pady=5)

        key_label = ttk.Label(temp_panel, text="{}:".format(key), style="rec_panel.TLabel", width=15)
        key_label.pack(side=LEFT, padx=5)

        temp_var = IntVar(); temp_var.set(0)
        checkbtn = ttk.Checkbutton(temp_panel, var=temp_var)
        checkbtn.pack(side=LEFT)

        return (key_label, checkbtn)

    # 根据某个ObjectCGIM更新信息面板
    def update_info_panel(self, object):
        str_attr_id = 0

        # 1.显示字符串的属性信息
        for key, value in object.str_attrs.items():
            self.rec_str_pair[str_attr_id][0].config(text="{}:".format(key))
            self.rec_str_pair[str_attr_id][1].config(text="{}".format(value))
            str_attr_id += 1

        for i in range(str_attr_id, self.max_str_attr_num):
            self.rec_str_pair[i][0].config(text=" ")
            self.rec_str_pair[i][1].config(text=" ")

        # for widget in self.info_panel.winfo_children()[self.max_attr_num:]:
        #     widget.destroy()

        # name是object.vars的key,用于找到是否显示这些rect
        # 这里是单个矩形框的删除/添加
        def get_checkbutton_command(name, rect, strmain=None):

            def checkbutton_command(event=None):
                if object.vars[name].get() == 0:
                    self.image_canv.delete(object.draw_ids[name])
                    if strmain is not None and len(strmain) >= 1:
                        self.image_canv.delete(object.draw_ids[list(strmain.keys())[0]])
                # 显示车牌
                else:
                    xmin, xmax = rect.xmin * image_width, rect.xmax * image_width
                    ymin, ymax = rect.ymin * image_height, rect.ymax * image_height
                    object.draw_ids[name] = self.image_canv.create_rectangle(xmin, ymin, xmax, ymax,
                                                                                       outline="red", width=3)
                    if strmain is not None and len(strmain) >= 1:
                        object.draw_ids[list(strmain.keys())[0]] = self.image_canv.create_text(xmin+5, ymin-20,
                                                    text=list(strmain.values())[0], fill="red", font=self.font)
            return checkbutton_command

        # 2.设置主包围框的checkbutton
        self.rec_rect_pair[0][0].config(text="{}:".format(object.rect_main.name))
        self.rec_rect_pair[0][1].config(var=object.vars[object.rect_main.name],
                                        command=get_checkbutton_command(
                                            object.rect_main.name, object.rect_main, strmain=object.str_main))

        # 3.显示其他辅助包围框
        rect_attr_id = 1
        for rect in object.rect_attrs:
            self.rec_rect_pair[rect_attr_id][0].config(text="{}:".format(rect.name))
            self.rec_rect_pair[rect_attr_id][1].config(var=object.vars[rect.name],
                                            command=get_checkbutton_command(rect.name, rect))
            rect_attr_id += 1

        # 这里是矩形框集合的删除/添加
        def get_checkbutton_command_list(name, rects):
            def checkbutton_command(event=None):
                if object.vars[name].get() == 0:
                    for id in object.draw_ids[name]:
                        self.image_canv.delete(id)
                # 显示车牌
                else:
                    for rect in rects:
                        xmin, xmax = rect.xmin * image_width, rect.xmax * image_width
                        ymin, ymax = rect.ymin * image_height, rect.ymax * image_height
                        object.draw_ids[name].append(self.image_canv.create_rectangle(xmin, ymin, xmax, ymax,
                                                                                      outline="red", width=2))
            return checkbutton_command

        # 4.显示包围框集合
        for key, value in object.rect_list_attrs.items():
            self.rec_rect_pair[rect_attr_id][0].config(text="{}:".format(key))
            self.rec_rect_pair[rect_attr_id][1].config(var=object.vars[key],
                                                           command=get_checkbutton_command_list(key, value))
            rect_attr_id += 1

        # 剩下的框清空显示
        for id in range(rect_attr_id, self.max_rect_attr_num):
            self.rec_rect_pair[id][0].config(text="")
            temp_var = IntVar();temp_var.set(0)
            self.rec_rect_pair[id][1].config(var=temp_var, command=None)

    # 根据原始字典形式的对象结果拆解并封装成多个ObjectCGIM对象,并对所有框设置对应的id(在canv上画图需要)
    # 再在显示画布上画出所有对象的主包围框
    def update_obj_and_rectIds(self, obj_dict):
        self.obj_list.clear()

        for id, element in enumerate(obj_dict):
            obj = ObjectCGIM(id, element)
            self.obj_list.append(obj)
            xmin, ymin, xmax, ymax = obj.rect_main.xmin * image_width, obj.rect_main.ymin * image_height,\
                                     obj.rect_main.xmax * image_width, obj.rect_main.ymax * image_height
            # 画出当前obj的主显示框
            obj.draw_ids[obj.rect_main.name] = self.image_canv.create_rectangle(xmin, ymin, xmax, ymax,
                                                                                outline="red", width=3)
            obj.draw_ids[list(obj.str_main.keys())[0]] = self.image_canv.create_text(xmin+5, ymin-20,
                                                    text=list(obj.str_main.values())[0], fill="red", font=self.font)
            obj.vars[obj.rect_main.name] = IntVar(); obj.vars[obj.rect_main.name].set(1)  # 主显示框是默认开始显示的

            for key in [r.name for r in obj.rect_attrs]+list(obj.rect_list_attrs.keys()):
                obj.vars[key] = IntVar()
                obj.vars[key].set(0)      # 默认辅助框是开始不显示的

    # 都是加载新图片时的操作:更新显示图片、删除所有画的矩形框、更新下拉框
    def update_image_panel(self):

        # 1.先删除原本的所有信息
        self.image_canv.delete(ALL)

        # 2.显示当前的新图片
        if self.video_cap is None:
            self.cur_image = misc.imread(self.all_image_paths[self.cur_image_id])
        else:
            self.video_cap.set(1, self.cur_image_id)
            ref, frame = self.video_cap.read()
            self.cur_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 3.1根据当前图片路径的id找到图片显示并进行识别得到识别结果
        engine_func = getattr(self.engine_modules[self.module_name], "engineKernel")
        # 这里做测试用,使用的是图片路径或者视频帧id,如下
        start_time = time.time()
        arg = self.all_image_paths[self.cur_image_id] if self.module_name == "engine_usalpr" else self.cur_image_id
        obj_dict = engine_func(arg)
        # 但是具体项目中可以使用图片数据(self.cur_image)传入engine_func函数
        # obj_dict = engineKernel(self.cur_image)
        end_time = time.time()

        # 3.2默认显示原图(不带有任何包围框之类，但是对于比如语义分割项目，tkinter没有专门画不规则语义区域的api，那么这里可以先在self.cur_image上画出来)
        self.image_PIL = ImageTk.PhotoImage(Image.fromarray(self.cur_image).resize((image_width, image_height)))
        self.image_canv.create_image(0, 0, image=self.image_PIL, anchor=NW)  # image参数必须是全局变量(如这里设置成类的对象属性)

        # 4.画出每个obj的主包围框，并给每个obj的其内每个rect设置id用于canv绘制矩形
        self.update_obj_and_rectIds(obj_dict)

        # 5.更新运行时间、"页码"、图片名称的label
        self.time_label.config(text="{:2.2f}ms".format((end_time - start_time) * 1000))
        self.num_label.config(text="{}/{}".format(self.cur_image_id + 1, self.images_number))

        # 更新信息显示窗口, 默认显示第一个对象的信息
        # 后面可以根据鼠标的移动调用update_info_panel函数显示对应对象的信息
        self.update_info_panel(self.obj_list[self.obj_id])

        # 6.更新图片列表
        self.update_image_list()

        # 7.如果达到视频最后一帧,那么将self.pause置为True
        if self.cur_image_id == self.images_number - 1:  # 达到视频最后一帧，就暂停
            self.pause = True

    # 根据当前图片的self.cur_image_id和self.all_image_paths更新图片列表
    def update_image_list(self):
        # 更新图片列表canvs中的图片
        self.list_image_pils = []
        self.list_images.clear()

        # 1.先获取图片列表的数据
        for id in range(self.cur_image_id - 2, self.cur_image_id + 3):
            if id < 0 or id >= self.images_number:
                self.list_images.append(self.empty_image.copy())
            else:
                if self.video_cap is None:     # 图片数据
                    self.list_images.append(misc.imread(self.all_image_paths[id]))
                else:
                    self.video_cap.set(1, id)
                    ref, frame = self.video_cap.read()
                    self.list_images.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # 2.根据图片列表显示图片
        for ind, cur_image in enumerate(self.list_images):
            self.list_image_pils.append(ImageTk.PhotoImage(Image.fromarray(cur_image).resize(
                (image_width // list_image_factor, image_height // list_image_factor))))

            self.image_list_canvs[ind].delete(ALL)
            self.image_list_canvs[ind].create_image(0, 0, image=self.list_image_pils[ind], anchor=NW)
        self.image_list_canvs[2].create_rectangle(5, 5, image_width // list_image_factor, image_height // list_image_factor,
                                                  outline="red", width=5)

    def create_image_list(self, list_frame):
        # 1.先建立好图片canvs
        self.image_list_canvs = []
        for ind in range(list_nums):
            image_canv = Canvas(list_frame, cursor='tcross')
            image_canv.pack(side=LEFT)
            image_canv.config(height=image_height // list_image_factor, width=image_width // list_image_factor)
            self.image_list_canvs.append(image_canv)

        for canv_id, change_num in zip([0, 1, 3, 4], [-2,-1,1,2]):
            self.image_list_canvs[canv_id].bind("<Button-1>", self.change_image(change_num))

        # 2.把图片填进去
        self.update_image_list()

if __name__ == '__main__':
    root = Tk()
    tool = USALPR(root)
    root.mainloop()
