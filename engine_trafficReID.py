import cv2
import json
json_file = 'test_data/traffic.json'
new_json_file = 'test_data/traffic_new.json'
video_file = 'test_data/video/traffic.mp4'

with open(new_json_file, 'r') as f:
    reid_result_dict = eval(f.read())

def show_old():
    with open(json_file, 'r') as f:
        traffic = eval(f.read())
    count = 1
    videoCapture = cv2.VideoCapture(video_file)
    ret, frame = videoCapture.read()
    ret, frame = videoCapture.read()

    while ret:
        ret, frame = videoCapture.read()
        h, w, _ = frame.shape
        for index in traffic[str(count)]:
            id = index["车辆Id_str"]
            cls = index["类别_str"]
            xc = float(index["车牌框_bbmain"].split(' ')[0])
            yc = float(index["车牌框_bbmain"].split(' ')[1])
            wn = float(index["车牌框_bbmain"].split(' ')[2])
            hn = float(index["车牌框_bbmain"].split(' ')[3].split('\n')[0])
            xmin = int((xc - wn / 2) * w)
            xmax = int((xc + wn / 2) * w)
            ymin = int((yc - hn / 2) * h)
            ymax = int((yc + hn / 2) * h)
            cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 1)
            cv2.putText(frame, id, (xmin,ymin), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
            cv2.putText(frame, cls, (xmin, ymax), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
        count += 1
        cv2.imshow('img', frame)
        cv2.waitKey(1)

def show_new():
    with open(new_json_file, 'r') as f:
        traffic = eval(f.read())

    videoCapture = cv2.VideoCapture(video_file)
    print(videoCapture.get(1), videoCapture.get(7))
    videoCapture.set(1, 0)
    ref, frame = videoCapture.read()
    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # for frame_id in range(2, int(videoCapture.get(7))):
    #     videoCapture.set(1, frame_id)
    #     ret, frame = videoCapture.read()
    #     h, w, _ = frame.shape
    #     for index in traffic[str(frame_id-1)]:
    #         id = index["车辆Id_str"]
    #         cls = index["类别_str"]
    #         xmin, ymin, xmax, ymax = [float(v) for v in index["车牌框_bbmain"].split(' ')]
    #         xmin, ymin, xmax, ymax = int(xmin*w), int(ymin*h), int(xmax*w), int(ymax*h)
    #
    #         cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 0, 255), 1)
    #         cv2.putText(frame, id, (xmin,ymin), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
    #         cv2.putText(frame, cls, (xmin, ymax), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
    #     cv2.imshow('img', frame)
    #     cv2.waitKey(100)

def engineKernel(frame_id):
    if frame_id>=2:
        frame_id-=1
    return reid_result_dict[str(frame_id)]

def change_mode():
    new_result = {}

    with open(json_file, 'r') as f:
        all_result = eval(f.read())
        for id, frame_res in all_result.items():
            cur_frame_new = []
            for single_res in frame_res:
                xc, yc, wn, hn = [float(v) for v in single_res["车牌框_bbmain"].split(" ")]
                xmin, ymin, xmax, ymax = xc-wn/2, yc-hn/2, xc+wn/2, yc + hn / 2
                single_res["车牌框_bbmain"] = "{} {} {} {}".format(xmin, ymin, xmax, ymax)
                single_res["车辆Id_strmain"] = single_res["车辆Id_str"]
                print(single_res)
                # print("车辆Id_str:{}->类别_str:{}->{}".format(single_res["车辆Id_str"],
                #                                           single_res["类别_str"], (xmin, ymin, xmax, ymax)))
                cur_frame_new.append(single_res)
            new_result[id] = cur_frame_new

    with open("test_data/traffic_new.json", "w") as fw:
        json.dump(new_result, fw, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    # change_mode()
    show_new()