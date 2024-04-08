from asterisk.manager import Manager
manager=Manager()
manager.connect('localhost')
manager.login('karan', 'test')
data="agi.py"
manager.originate(

        channel="SIP/9999",
        context="my-phones",
        exten="500",  # Assuming Zoiper is extension 100
        priority=1,
        caller_id="114",
        timeout=300000,  # Timeout in milliseconds
        #async=True  # Perform asynchronously
        application="AGI",
     #   application="Playback",
        data=data
    )