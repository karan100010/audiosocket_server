import astrisk
import uuid
import mylogging
#start a agi session

logger=mylogging.ColouredLogger()
agi=astrisk.AGI()

#start a audio socket server
# start a audio socket server
agi.stream_file('demo_audios/resp/1.wav', loop=True)