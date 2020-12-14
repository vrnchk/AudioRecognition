from dostoevsky.tokenization import RegexTokenizer
from dostoevsky.models import FastTextSocialNetworkModel
import os
tokenizer = RegexTokenizer()
model = FastTextSocialNetworkModel(tokenizer=tokenizer)

message0 = [
    'Добрый вечер фильм программа футбольный клуб в студию микрофона Максим курников а по видеосвязи Василию',
]
os.chdir('chunks_text_2')
num_chunks = 5
message = []
for i in range(num_chunks):
    fh = open("chunk"+str(i+1)+".txt", "r", encoding="utf-8")
    message.append(fh.read())
    fh.close()

results = model.predict(message, k=1)
for mes, sentiment in zip(message, results):
    print(sentiment)
    #for key in sentiment:
        #print(key)