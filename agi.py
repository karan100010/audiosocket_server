import astrisk
import uuid
import mylogging
#start a agi session

logger=mylogging.ColouredLogger()
agi=astrisk.AGI()

#start a audio socket server
agi.answer()
try:
    agi.appexec("AudioSocket("+uuid.uuid4+",localhost:1122)")
except:
    pass
    logger.info("AudioSocket is already running")


