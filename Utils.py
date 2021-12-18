import os
import glob
import numpy as np
from Rect import Rect

# 输入元素类型为Rect的list集合和IoU阈值,返回最终保留的rects下标
def NMS(org_rects, IoU_threshold):
    xmin = np.array([rect.xmin for rect in org_rects])
    ymin = np.array([rect.ymin for rect in org_rects])
    xmax = np.array([rect.xmax for rect in org_rects])
    ymax = np.array([rect.ymax for rect in org_rects])
    scores = np.array([rect.conf for rect in org_rects])

    areas = (xmax-xmin+1)*(ymax-ymin+1)

    #按照置信度从高到低排序
    order = scores.argsort()[::-1]
    keep_indices = []

    while order.size > 0:
        #order[0]是当前分数最大的窗口,肯定保留
        cur_max_socre_ind=order[0]
        keep_indices.append(cur_max_socre_ind)

        #计算窗口cur_max_socre_ind与其他窗口的重叠部分面积
        xxmin = np.maximum(xmin[cur_max_socre_ind], xmin[order[1:]])
        yymin = np.maximum(ymin[cur_max_socre_ind], ymin[order[1:]])
        xxmax = np.minimum(xmax[cur_max_socre_ind], xmax[order[1:]])
        yymax = np.minimum(ymax[cur_max_socre_ind], ymax[order[1:]])

        w = np.maximum(0.0,xxmax-xxmin+1)
        h = np.maximum(0.0,yymax-yymin+1)
        inter = w * h   #当前最大的rect与其他rects的相交面积

        union = areas[cur_max_socre_ind] + areas[order[1:]] - inter

        overlap = inter/union

        # 得到满足与当前最大得分的Rect交并比小于阈值的其他rects的原始下标inds
        # 下标的顺序还是一样的,即返回的原rects下标为inds[0]+1是当前score最大的rect
        # ps:  np.where返回的是展开后下标(indices),即indices[0]是所有满足条件的元素下标的第一维的值
        inds = np.where(overlap<=IoU_threshold)[0]

        # 之所加一的原因是由于overlap长度比order长度少1(不包含cur_max_socre_ind),
        # 所以inds+1对应到保留的窗口
        order = order[inds+1]
    dst_rects = [org_rects[ind] for ind in keep_indices]
    return dst_rects

# 通过中心padding的方式保证rect的宽高是2:1(不能强制resize)
# 返回的rect结果一定是不大于原rect范围的
def getPlateDoubleRate(rect:Rect, img_witdh:int, img_height: int):
    rect_w = rect.xmax - rect.xmin
    rect_h = rect.ymax - rect.ymin
    mid_x = (rect.xmin + rect.xmax) // 2
    mid_y = (rect.ymin + rect.ymax) // 2
    base = max(rect_w//4, rect_h//2)

    xmin = mid_x - base * 2
    xmax = mid_x + base * 2
    ymin = mid_y - base
    ymax = mid_y + base

    # 下面的额操作可能会导致索引出界
    if xmin < 0:
        xmin, xmax = 0, base*4
    if xmax > img_witdh:
        xmin, xmax = img_witdh - base * 4, img_witdh
    if ymin < 0:
        ymin, ymax = 0, base*2
    if ymax > img_height:
        ymin, ymax = img_height - base * 2, img_height
    return Rect(rect.name, xmin, ymin, xmax, ymax, rect.conf, (ymin+xmax) // 2)

# 将检测识别到的字符框反归一化到原来的整张图中(原来只是相对于车牌框的)
def normalizeRects(rects, base_rect):
    for rect in rects:
        rect.xmin += base_rect.xmin
        rect.xmax += base_rect.xmin
        rect.ymin += base_rect.ymin
        rect.ymax += base_rect.ymin


def glob_images(dir_path):
    image_exts = ["jpg", "png", "bmp", "jpeg"]
    image_paths = []
    for image_ext in image_exts:
        image_paths.extend(glob.glob(os.path.join(dir_path, "*.{}".format(image_ext))))
        image_paths.extend(glob.glob(os.path.join(dir_path, "*.{}".format(image_ext.upper()))))
    return image_paths

if __name__ == '__main__':
    print(glob_images("test_pics/temp"))
