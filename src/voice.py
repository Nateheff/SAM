import pyaudio
import time
from vosk import Model, KaldiRecognizer
import json
from threading import Thread
from queue import Queue
import requests
from vision.vision import vision

#TO DO:
"""
Try bigger/better speech-to-text models
Text yL group to bring jerseys
Debug server latency issue

DONE:
Add exception handling for incorrect/invalid SAM tokens
"""

BUFFER_SIZE = 1024
RECORD_SECONDS = 20

models = ["vosk-model-en-us-daanzu-20200905/vosk-model-en-us-daanzu-20200905", "vosk-model-en-us-0.22/vosk-model-en-us-0.22"]

model = Model(model_path=models[0])
recognizer = KaldiRecognizer(model, 16000)
recognizer.SetWords(True)
# print("Model loaded")
p = pyaudio.PyAudio()

stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                frames_per_buffer=BUFFER_SIZE)

frames = []

messages = Queue()
recordings = Queue()


# t_end = time.time() + RECORD_SECONDS

# while time.time() < t_end:
#     data = stream.read(BUFFER_SIZE)
#     frames.append(data)

"""

each time we get 5 more words, or 3 seconds pass, 
we check if
"""
def record():
    frames = []
    t_end = time.time() + 3
    while stream.is_active():
        data = stream.read(BUFFER_SIZE)
        frames.append(data)
        if time.time() > t_end:
            recordings.put(frames.copy())
            frames = []
            t_end = time.time() + 3
            print("Running")
        

thread_rec = Thread(target=record)
thread_rec.start()

def speech_rec(): 
    frames = recordings.get()
    recognizer.AcceptWaveform(b''.join(frames))
    result = recognizer.Result()
    text = json.loads(result)["text"]
    return text

# speech_rec()

def real_time_rec():
    try:
        text_full = ""
        has_sam = False
        
        sam_ind = 0
        while True:
            if not recordings.empty():
                text = speech_rec()

                text_full += " "+text
                
                print("FULL:",text_full)
                if has_sam:
                    #cut the full text to begin at sam
                    text_full = text_full[sam_ind:sam_ind + 15]
                    print(f"FINAL: {text_full}")
                    response = requests.request("POST","https://sam-image-post-j56rpdp2wa-uc.a.run.app/predict",json={"text": text_full})
                    print(response.text)
                    return response.text
                elif text_full.find(" sam ") != -1:
                    has_sam = True
                    sam_ind = text_full.find(" sam ")
                elif len(text_full) > 128 and text_full.find(" sam ") == -1:
                    text_full = ""
    except KeyboardInterrupt as e:
        stream.stop_stream()
        stream.close()
        p.terminate()
        exit()

        
        


            


                


# task = real_time_rec()
# stream.stop_stream()
# stream.close()
# p.terminate()
# if task == "1043":
#     vision()
# print("DONE: ",task)
# if __name__ == "__main__":
#     run()

        


