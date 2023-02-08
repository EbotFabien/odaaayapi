import requests
from bs4 import BeautifulSoup
import ssl



url='https://www.bbc.co.uk//news//uk-wales-64496535'
ssl._create_default_https_context = ssl._create_unverified_context
x = requests.get(url)

soup = BeautifulSoup(x.content, 'html.parser')
metas = soup.findAll('meta')
for i in metas:
    if i.get('property') == "og:image":
        thumbnail = i.get('content')

print(thumbnail)