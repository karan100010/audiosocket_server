#!/usr/bin/env python3
import playsound
from asterisk.agi import *
import time
import sys
import multiprocessing 
agi = AGI()

try:
    #stop_event = threading.Event()
    # Answer the call
    agi.answer()
    agi.verbose("python agi started")

    # Play the audio file
    #playsound.playsound("/home/vboxuser/output.wav")
    x=multiprocessing.Process(target=agi.stream_file,args=("/home/vboxuser/output",))
    x.start()
    time.sleep(5)
    #stop_event.set()
    multiprocessing.terminate()
    #my_thread.join()

    # Wait for the user to enter digits
    result = agi.wait_for_digit(5000)  # Timeout after 5000 milliseconds"

    # You can then handle the result as needed
    if result == -1:
        agi.verbose("User did not enter any digits")
    else:
        agi.verbose("User entered: " + chr(result))

except AGIException as e:
    agi.verbose(str(e))
