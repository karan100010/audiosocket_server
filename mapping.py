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
        "yes_intent_1": [("self.master", {"meta":"next_level"}),( "http://172.16.207:8084/give_phone", {"meta":"next_level"})],
        "yes_intent_2": [("http://172.16.1.207:5005/voice/20221205152448KQMS18_EH-M2.wav", {"meta":"next_level"}),( "http://172.16.207:8084/phone_given", {"meta":"switch_flow_to_0"})],
        "yes_intent_3": [(" http://172.16.1.207:8084/payment_link_sent.wav", {"meta":"hangup"})],
        "no_intent_1": [("http://172.16.1.207:8084/is_he_aviable", {"meta":"swich_flow"}),( "http://172.16.207:8084/please_share_alt", {"meta":"hangup"})],
        "no_intent_2": [("http://172.16.1.207:5005/voice/20230526112400HKP2VP_EH-M5.wav", {"meta":"hangup"}),( "http://172.16.207:8084/time_when_avl", {"meta":"hangup"})],
        "no_intent_3": [("http://172.16.1.207:5005/voice/202301021418523IWNWJ_EH-M2.wav", {"meta":"hangup"})],
        "call_back_later_intent_1": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"}),("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "call_back_later_intent_2": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"}),( "http://172.16.207:8084/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "call_back_later_intent_3": [("http://172.16.1.207:5005/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"}),( "http://172.16.207:8084/voice/20221205152848SB0SXI_EH-M2.wav", {"meta":"hangup"})],
        "other_intent_1": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "other_intent_2": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "other_intent_3": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}), ("http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_1": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_2": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],
        "contact_human_agent_intent_3": [("http://172.16.1.207:5005/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"}),( "http://172.16.207:8084/voice/20221213092638PSKL7I_EH-M5.wav", {"meta":"transfer"})],          
    },
    "utils":{
        "sorry": "http://172.16.1.207:5005/voice/20221205151448TZ19PK_EH-M2.wav",
        "bye": "http://172.16.1.207:5005/voice/2022122215292066Q8QZ_EH-M2.wav",
        "inttrupt": "http://172.16.1.207:8084/inttrupt.wav"
    "end_level": 4
}
}