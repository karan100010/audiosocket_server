from langdetect import detect


def is_language(text):
    try:
        detect(text)
        return True
    except:
        return False
        def is_english(text):
            try:
                lang = detect(text)
                return lang == 'en'
            except:
                return False