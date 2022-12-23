import requests
from bs4 import BeautifulSoup
import ssl



url='https://www.bbc.com/news/world'
ssl._create_default_https_context = ssl._create_unverified_context
x = requests.get(url)

soup = BeautifulSoup(x.content, 'html.parser')

print(soup)