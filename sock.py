import socket


import json
import numpy as np
from ultralytics import YOLO
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"

vision = YOLO()
vision = vision.to(device)

def process(frame: np.ndarray):
    
    
    results = vision.predict(frame, stream=False)
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
        return diff_boxes[min_idx]


def get_udp():
    # print("called")
    """
    
    """
    
    # hostname = socket.gethostname()
    # IPAddr = socket.gethostbyname(hostname)
    
    
    # IPAddr = "34.66.79.202"
    # IPAddr = "127.0.0.1"
    # 35.239.4.161
    # IPAddr = "34.41.250.194"
    IPAddr = ''
    UDP_PORT = 8080
    # TCP_PORT=80
    # print(IPAddr)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
    


    sock.bind((IPAddr, UDP_PORT)) #"34.41.250.194"
    

    # print(sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF))
    
    # print("SOCK UP")
    data_full = None
    recieved = []
    try:
        
        while True:
        # for _ in range(32):
            try:
                
                data, addr = sock.recvfrom(46080)
                
                # print(data[0])
                
                # print(sys.getsizeof(data))
                img_piece = data[0]
                # print(data[1:100])
                # print(img_piece)
                if img_piece in recieved:
                    sock.sendto(img_piece.to_bytes(), addr)
                    # print("sent ack")
                    continue
                else:
                    recieved.insert(0,img_piece)
                    sock.sendto(img_piece.to_bytes(), addr)
                    # print("sent ACK")
                    
                data = np.frombuffer(data,dtype=np.uint8, count=-1, offset=1)
                if data_full is None:
                    data_full = data
                else:
                    # print(data)
                    # print(data_full)
                    # print(data_full.shape)
                    data_full = np.concatenate((data_full, data), axis=0)
                
                
                if img_piece == 31:
                    # print(data_full)
                    data_full = data_full.reshape((480,640,3))

                if data_full.shape[0] == 480:
                    # print(data_full)
                    
                    min_diff = process(data_full)
                    
                    data_full = None
                    recieved = []
                    # print(min_diff)
                    if min_diff is None:
                        packet = np.zeros((1))
                        sock.sendto(packet.tobytes(), (addr))
                        continue
                    packet = min_diff.numpy().tobytes()
                    # print(sys.getsizeof(packet))
                    sock.sendto(packet, (addr))
                    
                    # print("sent")
                    # sock.close()
                    # return
                
                # if len(s) == (46080*20):
                #     frame = np.fromstring(s, dtype=np.uint8)
                #     frame = frame.reshape(480,640,3)
                #     cv2.imshow("frame",frame)

                #     s=""
                # if cv2.waitKey(1) & 0xFF == ord('q'):
                #     break
                
            except KeyboardInterrupt as e:
                print(e)
                sock.close()
                break
    except KeyboardInterrupt as e:
        print(e)
    finally:
        sock.close()


def get_tcp():

    IPAddr = ''
    TCP_PORT = 8000

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    sock.bind((IPAddr, TCP_PORT))
    sock.listen(5)
    # try:
    accepted_sock, addr = sock.accept()
    while True:
        # try:
        # accepted_sock, addr = sock.accept()
        data = b''
        while True:
            data += accepted_sock.recv(921600)
            if len(data) == 921600:
                break
        # print(len(data), data[65394:65494])
        data = np.frombuffer(data,dtype=np.uint8, count=-1, offset=0) 
        # print(data.size) #65495 sometimes
        data = data.reshape((480,640,3))
        #data is just one long array so needs to be reshaped like before``
        # print(data)
        min_diff = process(data)
        accepted_sock.send(min_diff.numpy().tobytes())
    # accepted_sock.close()

    #         except KeyboardInterrupt as e:
    #                 print(e)
    #                 sock.close()
    #                 break
    # except KeyboardInterrupt as e:
    #     print(e)
    # finally:
    #     sock.close()


# if __name__ == "__main__":
#     get_udp()