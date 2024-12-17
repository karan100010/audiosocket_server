mapping={
        "en":[{"welcome":["demo_audios/en/rec1_eng.wav"],
               "positive":["demo_audios/en/main_flow/positive/rec5_eng.wav","demo_audios/en/main_flow/positive/rec8_eng.wav","end_call"],
                "negative":["change_flow","demo_audios/en/main_flow/negative/rec9_eng.wav","end_call"]},
                
                {"welcome":["demo_audios/en/side_flow/rec2_eng.wav"],
                 "positive":["demo_audios/en/side_flow/positive/rec3_eng.wav","demo_audios/en/side_flow/positive/rec3_eng.wav","change_flow"],
                 "negative":["demo_audios/en/side_flow/negative/rec6_eng.wav","demo_audios/en/side_flow/negative/rec7_eng.wav","end_call"]},
                 ],

         

         "hi":[{"welcome":["demo_audios/hi/rec1_hin.wav"],
               "positive":["demo_audios/hi/main_flow/positive/rec5_hin.wav","demo_audios/hi/main_flow/positive/rec8_hin.wav","end_call"],
                "negative":["change_flow","demo_audios/hi/main_flow/negative/rec9_hin.wav","end_call"]},
                    
                    {"welcome":["demo_audios/hi/side_flow/rec2_hin.wav"],
                    "positive":["demo_audios/hi/side_flow/positive/rec3_hin.wav","demo_audios/hi/side_flow/positive/rec3_hin.wav","change_flow"],
                    "negative":["demo_audios/hi/side_flow/negative/rec6_hin.wav","demo_audios/hi/side_flow/negative/rec7_hin.wav","end_call"]}],

        "utils":{"hi":["demo_audios/rec11_hin.wav","demo_audios/rec10_hin.wav"],
        "en":["demo_audios/rec11_eng.wav","demo_audios/rec10_eng.wav"],
        "welcome":["demo_audios/rec11_eng.wav","demo_audios/rec10_eng.wav"],

        "common":[]}
        }
testmapping=[1,2,3]

map_mongo={
    "main_audios":{
        "yes_intent_1": [("self.master", {"meta":"next_level"}),( "http://172.16.1.207:8084/give_phone.wav", {"meta":"next_level"})],
        "yes_intent_2": [("http://172.16.1.207:5005/voice/20221205152448KQMS18_EH-M2.wav", {"meta":"next_level"}),( "http://172.16.1.207:8084/phone_given.wav", {"meta":"switch_flow_to_0"})],
        "yes_intent_3": [(" http://172.16.1.207:8084/payment_link_sent.wav", {"meta":"hangup","silence":False})],
        "no_intent_1": [("http://172.16.1.207:8084/is_he_aviable.wav", {"meta":"swich_flow"}),( "http://172.16.1.207:8084/please_share_alt.wav", {"meta":"hangup","silence":True})],
        "no_intent_2": [("http://172.16.1.207:5005/voice/20230526112400HKP2VP_EH-M5.wav", {"meta":"hangup","silence":True}),( "http://172.16.1.207:8084/time_when_avl.wav", {"meta":"hangup"})],
        "no_intent_3": [("http://172.16.1.207:5005/voice/202301021418523IWNWJ_EH-M2.wav", {"meta":"hangup","silence":True})],
        "call_back_later_intent_1": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup","silence":False}),("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "call_back_later_intent_2": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup","silence":False}),( "http://172.16.1.207:8084/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "call_back_later_intent_3": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup","silence":False}),( "http://172.16.1.207:8084/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "other_intent_1": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "other_intent_2": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "other_intent_3": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}), ("http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_1": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_2": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_3": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.1.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],          
    },
    "utils":{
        "sorry": "http://172.16.1.207:5005/voice/20221205151448TZ19PK_EH-M2.wav",
        "bye": "http://172.16.1.207:5005/voice/2022122215292066Q8QZ_EH-M2.wav",
        "inttrupt": "http://172.16.1.207:8084/inttrupt.wav"},
        
    "end_level": 4,
    "lang":"en"
}



map_mongo_hi = {
    "main_audios": {
        "yes_intent_1": [("self.master", {"meta": "next_level"}), ("http://172.16.1.207:8084/hi_give_phone.wav", {"meta": "next_level"})],
        "yes_intent_2": [("http://172.16.1.207:8084/hi_20221205152448KQMS18_EH-M2.wav", {"meta": "next_level"}), ( "http://172.16.1.207:8084/hi_phone_given.wav", {"meta": "switch_flow_to_0"})],
        "yes_intent_3": [( "http://172.16.1.207:8084/hi_payment_link_sent.wav", {"meta": "hangup"})],

        "no_intent_1": [( "http://172.16.1.207:8084/hi_is_he_aviable.wav", {"meta": "swich_flow"}), ( "http://172.16.1.207:8084/hi_please_share_alt.wav", {"meta": "hangup", "silence": True})],
        "no_intent_2": [( "http://172.16.1.207:8084/hi_20230526112400HKP2VP_EH-M5.wav", {"meta": "hangup", "silence": True}), ( "http://172.16.1.207:8084/hi_time_when_avl.wav", {"meta": "hangup"})],
        "no_intent_3": [( "http://172.16.1.207:8084/hi_202301021418523IWNWJ_EH-M2.wav", {"meta": "hangup", "silence": True})],

        "call_back_later_intent_1": [( "http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2.wav", {"meta": "hangup", "silence": False}), ( "http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2.wav", {"meta": "hangup"})],
        "call_back_later_intent_2": [( "http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2.wav", {"meta": "hangup", "silence": False}), ("http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2.wav", {"meta": "hangup"})],
        "call_back_later_intent_3": [( "http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2.wav", {"meta": "hangup", "silence": False}), ( "http://172.16.1.207:8084/hi_20221205152848SB0SXI_EH-M2", {"meta": "hangup"})],

        "other_intent_1": [("http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],
        "other_intent_2": [("http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],
        "other_intent_3": [("http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],

        "contact_human_agent_intent_1": [( "http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"}), ( "http://172.16.1.207:8084/voice/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],
        "contact_human_agent_intent_2": [( "http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"}), ( "http://172.16.1.207:8084/voice/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],
        "contact_human_agent_intent_3": [( "http://172.16.1.207:8084/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"}), ( "http://172.16.1.207:8084/voice/hi_20221213092638PSKL7I_EH-M5.wav", {"meta": "transfer"})],
    },
    "utils": {
        "sorry": ( "http://172.16.1.207:8084/hi_20221205151448TZ19PK_EH-M2.wav"),
        "bye": ( "http://172.16.1.207:8084/hi_2022122215292066Q8QZ_EH-M2.wav"),
        "inttrupt": ( "http://172.16.1.207:8084/hi_inttrupt-M2.wav")},

    "end_level": 4,
    "lang": "hi"
}

system_prompt = """ 
You are a paying role of a Assistent strictly who is in a phone conversation to recover loan wait for the user after you have said your part. Do not genrate User response
Follow the given steps. Stoping text genration after each step for the customer to respond. Stop genrating after line break:
You have to genrate one line rather then the whole conversation. Genrate the next line based on the User response. You might get a response in hindi or english respond in the
language that the User is using. Use <end> in the end of the line when you feel you need to end the conversation. Use <transfer> when 
you feel you need to bring a human on the line. Use the same langauage as the last message by the customer 

1. **Confirm Identity**:  
   - Greet the customer and confirm their identity by asking, "Hello, is this [Customer's Name]?"  
   - If they are not the person you are looking for ask for a diffrent time when the person will be avaiable
   - If they are the person proceed to step 2
   - If they say it is a wrong number respond with saying that you will not call here again.
   - If you do not undersand what they are saying ask politely if they could repeat themselves
   - If the user askes to talk to someone else use the <trasfer> tag  Example: I will transfer your call <transfer>  
   - Answer only policy related questions if the response is not policy related respond with "I dont know that" 
   - Exmaple:  Hello, is this John Doe?

2. **Ask for Payment**:  
   - Politely remind them about the overdue payment, specifying the amount and account details. Ask if they can make the payment today.  
   - If they say it is a wrong number respond with saying that you will not call here again.
   - If you do not undersand what they are saying ask politely if they could repeat themselves
   - If they say it is a wrong number respond with saying that you will not call here again.
   - If you do not undersand what they are saying ask politely if they could repeat themselves
   - If the user askes to talk to someone else use the <trasfer> tag  Example: I will transfer your call <transfer>  
   - Answer only policy related questions if the response is not policy related respond with "I dont know that "  
   - Example: Please confirm if you can make the payment now?
   

3. **Confirm Payment Method**:  
   - If they agree to pay, inquire about their preferred payment method and provide available options (e.g., online transfer, UPI, cheque).  
   - If they cannot pay today, suggest a payment plan or alternative arrangement.  
   - If they say it is a wrong number respond with saying that you will not call here again.
   - If you do not undersand what they are saying ask politely if they could repeat themselves
   - If the user askes to talk to someone else use the <trasfer> tag  Example: I will transfer your call <transfer>  Example: I will transfer your call <transfer>
   - Answer only policy related questions if the response is not policy related respond with "I dont know that"  
   - Example: How would you like to pay?

4. **Give Regards and Hang Up**:  
   - End the conversation respectfully, thanking them for their cooperation or understanding.  
   - If they say it is a wrong number respond with saying that you will not call here again.
   - If you do not undersand what they are saying ask politely if they could repeat themselves
   - If the user askes to talk to someone else use the <trasfer> tag  Example: I will transfer your call <transfer>  
   - Answer only policy related questions if the response is not policy related respond with "I dont know that "   
   - Example closing messages:  
     - If payment is agreed upon: "Thank you for your cooperation. Please let us know once the payment is completed. Have a great day ahead!"  
     - If payment is not resolved: "Thank you for speaking with me. Please contact us if you need further assistance. Have a good day!"  
 

Always maintain a calm and respectful tone throughout the conversation.
Follow the example given below:

Example 1:

Assistent: नमस्ते, क्या मैं करन जोशी से बात कर रहा हूँ?
User: जी हाँ
Assistent: आपके भुगतान की राशि बकाया है, क्या आप अभी भुगतान करना चाहेंगे?
User: हाँ
Assistent: आप भुगतान किस माध्यम से करना चाहेंगे?
User: क्रेडिट कार्ड
Assistent: मैं आपको लिंक भेज रहा हूँ, कृपया भुगतान कर दें।<end>

Example 2:

Assistent: नमस्ते, क्या मैं करन जोशी से बात कर रहा हूँ?
User: नहीं
Assistent: क्या आप मुझे करन से अभी बात करवा सकते हैं?
User: नहीं
Assistent: मैं करन से कब बात कर सकता हूँ, कब कॉल करूँ?
User: कल
Assistent: ठीक है, मैं कल कॉल करूँगा। आपका दिन शुभ हो।<end>

Example 3:

Assistent: नमस्ते, क्या मैं करन जोशी से बात कर रहा हूँ?
User: झग्जहब्शद फ्कजस्जफ
Assistent: क्षमा करें, मैं समझ नहीं पाया कि आपने क्या कहा। मैं आपको अपने सलाहकार से जोड़ रहा हूँ।<transfer>

Example 4:

Assistent: नमस्ते, क्या मैं करन जोशी से बात कर रहा हूँ?
User: नहीं, यह गलत नंबर है।
Assistent: क्षमा करें, हम आपको दोबारा कॉल नहीं करेंगे और इस नंबर को ब्लॉक कर रहे हैं।<end>




"""


# Initialize the conversation messages
messages=[{
  "role": "system",
  "content": (system_prompt
  )}
,{"role": "assistent",
  "content":"नमस्ते, क्या मैं करन जोशी से बात कर रहा हूँ?"

}
]