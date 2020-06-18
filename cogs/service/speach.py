from gtts import gTTS

def tell(phrase,lang='ru'):
     tts_ru = gTTS(phrase, lang=lang,)
     f = open('output.mp3', 'wb')
     f.close()
     with open('output.mp3', 'wb') as f:
          tts_ru.write_to_fp(f)
     return 'output.mp3'