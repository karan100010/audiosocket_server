#!/usr/bin/env python3
from asterisk.agi import AGI
#start a agi session
import uuid


agi= AGI()

#start a audio socket server
# start a audio socket server
agi.stream_file('demo_audios/resp/1')
agi.exec_command("Audiosocket",[str(uuid.uuid4()),"localhost:1122"])
agi.stream_flie("demo_audios/resp/2")
agi.hangup()