import torch

import cv2
from ultralytics import YOLO

from test import track
import requests
from send_udp import send_data, send_tcp

import numpy as np
import socket
import time


# host = "192.168.0.1"

# model = YOLO()
stream = cv2.VideoCapture(0)


def vision_api():
    global stream
    
    if not stream.isOpened():
        stream = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    while(True):
        # print("in loop")
        #frame is a 480 x 640 x 3 array
        
        ret, frame = stream.read()
       
        # results = model.predict(frame, stream=False)
        frame = frame.tolist()
        
        response = requests.post("http://localhost:5000/vision", json={"img":frame})
        results, min_idx = response.json()
        # results = model.predict(frame, stream=False)
            
        speed, right, left = track(results[min_idx], results[min_idx] > 0)
        print(f"MOVE {"RIGHT" if right else "LEFT"} at {speed} SPEED!")


        # cv2.imshow('video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()

    cv2.destroyAllWindows()

def vision_socket():
    global stream
    try:
        if not stream.isOpened():
            stream = cv2.VideoCapture(0,cv2.CAP_DSHOW)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(('127.0.0.1',8000))
        # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        while(True):
            # print("in loop")
            #frame is a 480 x 640 x 3 array

            ret, frame = stream.read()
            
            frame = np.array(frame)
            # print(frame.size)
            # results = model.predict(frame, stream=False)
            # frame = np.split(frame, 32, axis=0)
            time_start = time.time()
            results = send_tcp(frame,sock)#, host="34.46.63.237"
            print(f"TIME DATA: {time.time()-time_start}")
            # print(results)
            if results == 0:
                continue
            # response = requests.post("http://localhost:5000/vision", json={"img":frame})
            
            # response = send_data(frame, port=8080)
            # response = None
            # results, min_idx = response.json()
            # results = model.predict(frame, stream=False)
                
            speed, right, left = track(results, results > 0)
            
            print(f"MOVE {"RIGHT" if right else "LEFT"} at {speed} SPEED!")


            # cv2.imshow('video', frame)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
    except Exception as e:
        print(e)
    finally:
        stream.release()
        sock.close()

def vision():

    global stream
    
    if not stream.isOpened():
        stream = cv2.VideoCapture(0,cv2.CAP_DSHOW)
    while(True):
        print("in loop")
        #frame is a 480 x 640 x 3 array
        ret, frame = stream.read()

        
        results = model.predict(frame, stream=False)
        
        for result in results:
            person_indexes = (result.boxes.cls == 0).nonzero() #get the index of objects which are humans (class == 0)
            if len(person_indexes) == 0:
                continue
            person_indexes = person_indexes.tolist()[0] #turn the indexes into a list so we can use them to index into boxes

            #DRAW BOUNDING BOX CODE ---

            # xy1 = result.boxes.xyxy[person_indexes, :2]
            # xy2 = result.boxes.xyxy[person_indexes, 2:]
            # xy1 = xy1.int()
            # xy2 = xy2.int()
            # xy1 = tuple(xy1.tolist()[0])
            # xy2 = tuple(xy2.tolist()[0])
            # frame = cv2.rectangle(frame,xy1,xy2,(0,0,255), thickness=5)

            # ---

            boxes = result.boxes.xywhn[person_indexes] #get the x, y, width, height normalized box data for each detected person
            # print(boxes)

            door_box = [0.5,0.5]
            diff_boxes = boxes[:,0] - door_box[0]
            if len(diff_boxes) > 1:
                diff_abs = torch.abs(diff_boxes)
                min_dist, min_idx = diff_abs.min()
            else:
                min_idx = 0
            
            speed, right, left = track(diff_boxes[min_idx], diff_boxes[min_idx] > 0)
            print(f"MOVE {"RIGHT" if right else "LEFT"} at {speed} SPEED!")
            # if diff_boxes[min_idx] > 0:
            #     # print("RIGHT")
            # else:
            #     # print("LEFT")
            #IN THE END: return diff_boxes[min_idx] (send it to the turret somehow)

            cv2.imshow('video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    stream.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    vision_socket()

    