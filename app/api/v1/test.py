from breadability.readable import Article

from sumy.parsers.html import HtmlParser
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
import requests
from bs4 import BeautifulSoup

lang="english"
url='https://edition.cnn.com/2022/01/11/politics/biden-atlanta-voting-rights-speech/index.html'

x = requests.get(url)
if x is not None:
    
    soup = BeautifulSoup(x.content, 'html.parser')   
    document= Article(x.content, url)
    text=document.readable
def sup(cont,n):
    sum_content=''
    parser = HtmlParser.from_string(cont, '', Tokenizer(lang))
    #parser = HtmlParser.from_url(url, Tokenizer(lang))
    stemmer = Stemmer(lang)
    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(lang)

    for sentence in summarizer(parser.document,n):
        sum_content += '\n'+str(sentence)

    #print(text)
    #print('='*30)
    return sum_content

subtext=sup(text,20)
print(subtext)
print('='*30)
print(sup(subtext,2))








