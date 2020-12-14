# -*- coding: utf-8 -*-
"""audio_version2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1YEFyDW72uiRMg0465AAmwlytI_ZLkjla

**Подготовка**

Все необходимые библиотеки загружаются на Gogle Drive, чтобы при перезапуске среды не приходилось заново их устанавливать.

*   pytube - для скачивания видео с youtube
*   pydub - для работы с самим аудиофайлом: перевод в нужное расширение, деление файла на несколько маленьких по тишине
*   SpeechRecognition - для перевода аудио в текст

Следующие ячейки с установкой библиотек нужно запустить только один раз, далее при перезапуске они уже будут подключены.
"""

!apt install ffmpeg

pip install pytube

import os, sys
from google.colab import drive
drive.mount('/content/mnt')
nb_path = '/content/notebooks'
os.symlink('/content/mnt/My Drive/Colab Notebooks', nb_path)
sys.path.insert(0, nb_path)  # or append(nb_path)

!pip install --target=$nb_path youtube_dl

!pip install --target=$nb_path pafy

!pip install --target=$nb_path SpeechRecognition

!pip install --target=$nb_path pydub

!pip install --target=$nb_path pytube

!apt install ffmpeg

!pip install dostoevsky
!python -m dostoevsky download fasttext-social-network-model

"""**Скачивание видео**

Данный код скачивает видео с youtube по ссылке.
"""

import os
os.chdir('/content')
from pytube import YouTube

YouTube("https://www.youtube.com/watch?v=hYNtL7YOUV8").streams.filter(only_audio=True).first().download(filename='audio')

"""**Получение аудио**

Данный код получает только аудио из видео.
"""

!ffmpeg -y -i audio.mp4 -ac 1 -f wav audio1.wav

"""**Деление аудио**



"""

import os
from pydub import silence, AudioSegment
import glob

MIN_SILENCE_LEN = 300
MIN_DURATION = 2000
DEBUG = 0

os.chdir('/content')
def read_audio(audio_path):
    audio = AudioSegment.from_file(audio_path)
    audio = audio.set_channels(1)

    return audio


def concatenate_edges(raw_interval):
    edges = [raw_interval[0]]

    # concatenate two edges if the interval btw them is too short
    for idx in range(1, len(raw_interval) - 1):
        cur_start = raw_interval[idx][0]
        prev_end = edges[-1][1]

        if cur_start - prev_end < MIN_SILENCE_LEN:
            edges[-1][1] = raw_interval[idx][1]
        else:
            edges.append(raw_interval[idx])

    return edges


def get_rid_of_short_intervals(edges):
    intervals = []

    for idx in range(len(edges)):
        if edges[idx][1]-edges[idx][0] > MIN_DURATION:
            intervals.append(edges[idx])

    return intervals


def splitAudioBySilence(audio_path, skip_idx=0, out_ext="wav", silence_thresh=-40, silence_chunk_len=100, keep_silence=100):
    audio = read_audio(audio_path)

    not_silence_ranges = silence.detect_nonsilent(
        audio, min_silence_len=silence_chunk_len,
        silence_thresh=silence_thresh)

    edges = concatenate_edges(not_silence_ranges)
    intervals = get_rid_of_short_intervals(edges)

    try:
        os.mkdir('audio_chunks6')
    except(FileExistsError):
        pass
    os.chdir('audio_chunks6')

    files = glob.glob('/content/audio_chunks6/*')
    for f in files:
        os.remove(f)

    for idx, (start_idx, end_idx) in enumerate(intervals[skip_idx:]):
        start_idx = max(0, start_idx - keep_silence)
        end_idx += keep_silence
        
        segment = audio[start_idx:end_idx]
        segment.export(".//chunk{0}.mp3".format(idx), out_ext)
        segment.set_channels(1)
        segment.export(".//chunk{0}.wav".format(idx), format="wav")
        os.remove(".//chunk{0}.mp3".format(idx))

splitAudioBySilence("audio1.wav")

"""**Скачивание аудио по предложениям и распознавание текста каждого**

С помощью функции recognize_google() распознаем текст. Распознавание от Google - самое качественное и удобное из тех, что предоставляет библиотека SpeechRecognition, поэтому выбрано именно оно. Запись распознанных предложений ведется в файлы.
"""

import speech_recognition as sr
def recognizeSpeech():
    os.chdir('/content')
    try:
        os.mkdir('sentences')
    except(FileExistsError):
        pass
    files = glob.glob('/content/sentences/*')
    for f in files:
        os.remove(f)
    test = os.listdir("audio_chunks6")
    for filename in test:
        if filename.endswith(".wav"): 
            r = sr.Recognizer()
            filenameWithoutFormat = filename[:-4]
            with sr.AudioFile("./audio_chunks6/" + filename) as source:
                audio = r.record(source)
                try:
                    rec = r.recognize_google(audio, language="ru")
                    f = open("./sentences/" + filenameWithoutFormat + "_sentence" + ".txt", "w+")
                    f.write(rec)
                    f.close()
                except sr.UnknownValueError:
                    pass
                    #print("Could not understand audio")
                except sr.RequestError as e:
                    print("Could not request results. check your internet connection. Error: ", e)
            continue
        else:
            continue
recognizeSpeech()

from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import os
tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

os.chdir('/content')
message = []
test = os.listdir("sentences")
i = 0
os.chdir('sentences')
for filename in test:
    try:
        fh = open("chunk"+str(i)+"_sentence.txt", "r", encoding="utf-8")
        message.append(fh.read())
        fh.close()
    except:
        i += 1
        pass

os.chdir('/content')
results = model.predict(message, k=1)
i = 0
for mes, sentiment in zip(message, results):
    f = open("./sentences/" + "chunk"+str(i)+ "_sentence.txt", "a")
    f.write('\n')
    f.write(str(sentiment))
    f.close()
    i += 1