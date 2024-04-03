import astrisk

import mylogging
#start a agi session
import uuid

logger=mylogging.ColouredLogger()
agi=astrisk.AGI()

#start a audio socket server
# start a audio socket server
agi.stream_file('demo_audios/resp/1.wav')
agi.exec_command("Audiosocket",[str(uuid.uuid4()),"localhost:1122"])
agi.stream_flie("demo_audios/resp/2.wav")
agi.hangup()