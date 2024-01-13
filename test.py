from time import sleep
from audiosocket import *
import numpy as np
import webrtcvad
from mylogging import ColouredLogger
import wave
import threading
import sys
import requests
from mapping import *
import math
from req import Requsts
import json
import base64
from example_application import AudioStreamer

# stream=AudioStreamer()
# while stream.conn.connected:
#     data=stream.conn.read()
#     req={"audiofile":base64.b64encode(data).decode('utf-8')}
#     requests.post("http://localhost:5000/audio",json=req)