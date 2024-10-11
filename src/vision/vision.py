import cv2
import torch
import numpy as np
import time

from YoloFastestV2.detector import Detector
import utils.utils
from motor_rpi4 import motor_init, move, stop
from tracking import track
from gun_rpi4 import *


model = Detector()
model.load_state_dict(torch.load("modelzoo/coco2017-0.241078ap-model.pth", map_location="cpu"))
model.eval()

stream = cv2.VideoCapture(0)

def process(img):
    preds = model(img)
    output = utils.utils.handel_preds(preds,"cpu")
    # print(output)
    output_boxes = utils.utils.non_max_suppression(output, conf_thres = 0.3, iou_thres = 0.4)
    
    # print(output_boxes)
    for box in output_boxes[0]:
        box = box.tolist()

        center = (box[0] + box[2]) / 2.0
        # print(center)
        if box[5] == 0.0:
            return (center - 176.0) / 176.0
    return 0


def vision():
        global stream
        try:
            if not stream.isOpened():
                stream = cv2.VideoCapture(0,cv2.CAP_DSHOW)

            time_end = time.time() + 21
            motor_init()
            gun_init()
            fire()
            while time.time() < time_end:

                ret, frame = stream.read()

                data = cv2.resize(frame, (352,352), interpolation = cv2.INTER_LINEAR)
                img = data.reshape(1, 352, 352, 3)
                img = torch.from_numpy(img.transpose(0,3, 1, 2))
                img = img.float() / 255.0
                #data is just one long array so needs to be reshaped like before``
                # print(data)
                min_diff = process(img)
                if min_diff == 0:
                    continue

                speed = track(min_diff)
                direction = min_diff > 0
                move(speed, direction)
            cease_fire()
        except Exception as e:
            print(e)
        finally:
            stream.release()
            stop()
            cease_fire()

"""
add test function
change paths of files in backbone and here
get venv going
download all the requirements (torch,numpy,cv2, torchvision,gpiozero,lgpio,etc.)
change speed and direction
"""
            