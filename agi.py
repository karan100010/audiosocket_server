#!/usr/bin/env python3
from asterisk.agi import AGI
#start a agi session
import uuid


agi= AGI()

#start a audio socket server
# start a audio socket server
agi.stream_file('/home/vboxuser/audiosocket_server/demo_audios/resp/1')
agi.exec_command("Dial","(AudioSocket/localhost:1122/${SIP_HEADER(Call-ID)},,g")
#agi.exec_command("Verbose","audiosocket has ended")
agi.stream_flie("/home/vboxuser/audiosocket_server/demo_audios/resp/2")
agi.hangup()