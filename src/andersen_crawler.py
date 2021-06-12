import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from tqdm.auto import tqdm
from pathlib import Path


base_url = 'https://www.andersenstories.com/da/andersen_fortaellinger/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'}
html = requests.get(base_url + 'list', headers=headers)
soup = BeautifulSoup(html.content, 'html.parser')
ul = soup.find('ul', class_='bluelink')
links = [base_url + a['href'] for a in ul.find_all('a', href=True)]

path = Path('data') / 'output.txt'
if not path.exists():
    path.touch()

for link in tqdm(links):
    article = Article(link)
    article.download()
    article.parse()
    doc = article.text
    doc = re.sub('"', '', doc)
    doc = re.sub('! *', '!\n', doc)
    doc = re.sub(r'[:;.] *', '.\n', doc)
    doc = re.sub('\n+', '\n', doc)
    lines = [line for line in doc.split('\n')
                  if len(line.split()) >= 4 and
                     len(line.split()) < 14 and
                     len(re.sub('[^a-z]', '', line)) > 0]
    doc = '\n'.join(lines)

    with path.open('a') as f:
        f.write(doc + '\n')
