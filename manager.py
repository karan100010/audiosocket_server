from asterisk.manager import Manager
manager=Manager()
manager.connect('localhost')
manager.login('karan', 'test')
data="/home/vboxuser/audiosocket_server/agi.py"
manager.originate(

        channel="SIP/zoiper",
        context="my-phones",
        exten="500",  # Assuming Zoiper is extension 100
        priority=1,
        caller_id="114",
        timeout=300000,  # Timeout in milliseconds
        #async=True  # Perform asynchronously
        application="AGI",
       #application="Playback",
        data=data
    )
Action: Originate
Channel:  SIP/zoiper     ; Channel to dial, e.g., SIP/1001
Context:      ; Context to start the dialplan, e.g., default
Exten: <extension>       ; Extension to dial, e.g., 1002
Priority: <priority>     ; Priority to start at in the context, e.g., 1
CallerID: <callerid>     ; Caller ID to use, e.g., "John Doe" <1234>
Timeout: <timeout>       ; Maximum time to wait for call to be answered (in milliseconds), e.g., 30000

Action: Originate
Channel: SIP/9999
Context: my-phones
Exten: 500
Priority: 1
CallerID: 114
Timeout: 300000
Application: Playback
Data: hello-world