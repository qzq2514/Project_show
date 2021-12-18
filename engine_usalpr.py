import os
import json
from ObjectCGIM import ObjectCGIM

# 根据一张车牌图像的路径，读取图像，然后进行车牌识别返回字典形式的车牌

with open("test_data/lpr_res.json", "r") as fr:
    lpr_result_dict = json.load(fr)

def engineKernel(image_path):
    image_name = os.path.basename(image_path)
    return lpr_result_dict[image_name]

if __name__ == '__main__':
    ret = engineKernel("test_data/pics/multi.png")
    # print(ret)
    obj = ObjectCGIM(1, ret[0])
    print(list(obj.str_main.keys())[0])
    print(list(obj.str_main.values())[0])

