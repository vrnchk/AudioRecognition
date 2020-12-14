import pafy
import os
import speech_recognition as sr
from os import path
import os
from pydub import AudioSegment
from pydub.silence import split_on_silence
url = "https://www.youtube.com/watch?v=_7fsATsADIE"
result = pafy.new(url)
best_quality_audio = result.getbestaudio()

best_quality_audio.download()
print('Downloaded')
name = result.title
name = name.replace('/', '_')
name = name.replace('//', '__')
os.rename(name+'.webm', 'au.webm')

webw_audio = AudioSegment.from_file("au.webm", format="webm")
webw_audio.export("audio1.wav", format="wav")

path = "audio1.wav"
song = AudioSegment.from_wav(path)

chunks = split_on_silence(song, min_silence_len = 2000, silence_thresh = -19)
try:
    os.mkdir('audio_chunks')
except(FileExistsError):
    pass

os.chdir('audio_chunks')

fh = open("recognized.txt", "w")
#os.chdir('audio_chunks6')
for i, chunk in enumerate(chunks):
    silence_chunk = AudioSegment.silent(duration=500)
    audio_chunk = silence_chunk + chunk + silence_chunk
    normalized_chunk = match_target_amplitude(audio_chunk, -20.0)
    #print("Exporting chunk{0}.wav.".format(i))
    normalized_chunk.export(".//chunk{0}.wav".format(i), bitrate = "192k", format = "wav")
    filename = 'chunk'+str(i)+'.wav'
    #print("Processing chunk "+str(i))
    file = filename
    r = sr.Recognizer()
    # распознать кусок
    with sr.AudioFile(file) as source:
        audio = r.record(source)
    try:
        # попробуйте преобразовать его в текст
        rec = r.recognize_google(audio, language="ru")
        # записать вывод в файл.
        fh.write(rec+'\n')
        #print(rec)
    except sr.UnknownValueError:
        pass
        #print("Could not understand audio")
    except sr.RequestError as e:
        pass
        #print("Could not request results. check your internet connection")
fh.close()