import socket
import sys
import json
import numpy as np
import cv2

"""
Add which piece of image to eat data piece
Add checkksum 
Add verification process to ensure all piece of image make it

"""
def send_tcp(data:np.ndarray, sock, host="127.0.0.1", port=8000):
    # sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # sock.connect((host,port))
    # print(data.size)
    # data = data.tobytes()
    # print(len(data), data[65394:65494])
    sock.send(data)
    data = sock.recv(4)
    # print(data, len(data))
    final = np.frombuffer(data, dtype=np.float32, count=-1)
    return final[0]



def send_data(data:np.ndarray, sock, host="localhost", port=8080):
    # data
    # data = json.dumps(data)

     #UDP Socket (SOCK_DGRAM) over internet (AF_INET)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 8192)
    # print(f"in send: {host}:{port}")
    for i, data_piece in enumerate(data):
        # print("I: ",i)
        # print(sys.getsizeof(data_piece))
        # print(data_piece.dtype)
        data_piece:bytes = data_piece.tobytes()
        piece_number = i.to_bytes()
        
        packet = piece_number + data_piece
        # sock.sendto(packet, (host,port))

        while True:
            sock.sendto(packet, (host, port))
            # print("sent")
            check = sock.recv(1)
            # print(check)
            if check == piece_number:
                break


    # print("final check")  
    check = sock.recv(37)
    # print(check)
    check = np.frombuffer(check, dtype=np.float32, count=-1)
    # sock.close()
    return check[0]
    # received = sock.recv(1024)
    # received = received.decode()
    # print(received)


def get_udp():
    
    hostname = socket.gethostname()
    IPAddr = socket.gethostbyname(hostname)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 8192)
    UDP_PORT = 5000
    sock.bind((IPAddr, UDP_PORT))
    # print("SOCK UP")
    while True:
      data, addr = sock.recvfrom(46080)
      s+= data
      if len(s) == (46080*20):
          frame = np.fromstring (s, dtype=np.uint8)
          frame = frame.reshape(480,640,3)
          cv2.imshow("frame",frame)

          s=""
      if cv2.waitKey(1) & 0xFF == ord('q'):
          break


if __name__ == "__main__":
    pass