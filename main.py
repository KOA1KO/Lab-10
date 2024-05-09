import pyttsx3, pyaudio, vosk
import json, requests

text_to_speech = pyttsx3.init('sapi5')
available_voices = text_to_speech.getProperty('voices')
text_to_speech.setProperty('voices', 'en')

for voice in available_voices:
    print(voice.name)
    if voice.name == 'Microsoft Zira Desktop - English (United States)':
        text_to_speech.setProperty('voice', voice.id)

recognition_model = vosk.Model('vosk-model-small-en-us-0.15')
recognizer = vosk.KaldiRecognizer(recognition_model, 16000)
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=16000,
                    input=True,
                    frames_per_buffer=8000)
stream.start_stream()


def listen_to_user():
    while True:
        user_input = stream.read(4000, exception_on_overflow=False)
        if recognizer.AcceptWaveform(user_input) and len(user_input) > 0:
            result = json.loads(recognizer.Result())
            if result['text']:
                yield result['text']


def generate_speech(text):
    text_to_speech.say(text)
    text_to_speech.runAndWait()


word_data = None
word_term = None

for text in listen_to_user():
    if 'find' in text:
        word_term = text.split("find ")[1]
        try:
            response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/en/{word_term}')
            word_data = response.json()
            print(word_data['message'])
        except Exception as ex:
            print('The word', word_term, 'was found')
    elif text == 'definition':
        if word_data:
            print(word_data[0]['meanings'][0]['definitions'][0]['definition'])
            generate_speech(word_data[0]['meanings'][0]['definitions'][0]['definition'])
        else:
            print('No data for term')
    elif text == 'example':
        if word_data:
            try:
                print(word_data[0]['meanings'][0]['definitions'][0]['example'])
                generate_speech(word_data[0]['meanings'][0]['definitions'][0]['example'])
            except KeyError:
                print("No example found for this term")
        else:
            print('No data for term')
    elif text == 'save':
        if word_data:
            with open("dic.txt", "w") as file:
                json.dump(word_data, file)
            print("The data is saved to a file dic.txt")
        else:
            print('No data for term')
    elif text == 'source':
        if word_data:
            print(word_data[0]['sourceUrls'][0])
        else:
            print('No data for term')
    elif text == 'exit':
        break
    else:
        print('The command is not recognized')
