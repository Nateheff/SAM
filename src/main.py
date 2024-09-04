from voice import *


"""

recording thread is always going and sending stuff to our vosk/SAM api

when recording thread gets the signal to fire, we stop the recording thread and begin two new threads:
    fire thread
    move thread

we may not even need these to be separate threads as we can just

set firing pins to true
begin vision
run vision
turn off firing
turn off vision
"""

def run():
    
    while True:
        task = real_time_rec()
        try:
            match task:
                case "1043": #[TURRET]
                    vision()
                case "1032" | "1037" | "1049" | "1054": # [WEATHER] | [TIME] | [MUSIC] | [DATE]
                    raise(NotImplementedError("Functionality for this command has not yet been implemented."))
                case _:
                    raise(ValueError("The inputted prompt has produced an invalid token, suggesting the prompt was not a valid command. Please try to provide clear commands to the model for what task(s) you would like it to perform. For example: Sam play some music or Sam red alert."))
                
        except Exception as e:
            print(e)
        except KeyboardInterrupt as e:
            stream.stop_stream()
            stream.close()
            p.terminate()
            exit()