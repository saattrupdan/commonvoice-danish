'''Script that scrapes HC Andersen fairytales'''

import requests
from bs4 import BeautifulSoup
from newspaper import Article
import re
from tqdm.auto import tqdm
from pathlib import Path


def scrape_andersen():
    '''Scrape HC Andersen fairytales and store them in `data/output.txt`'''

    # Get the HTML from the website containing all the fairytales
    base_url = 'https://www.andersenstories.com/da/andersen_fortaellinger/'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) '
                             'Chrome/83.0.4103.61 Safari/537.36'}
    html = requests.get(base_url + 'list', headers=headers)

    # Parse the HTML and extract all the links for the individual fairytales
    soup = BeautifulSoup(html.content, 'html.parser')
    ul = soup.find('ul', class_='bluelink')
    links = [base_url + a['href'] for a in ul.find_all('a', href=True)]

    # Create the output file if it does not already exist
    path = Path('data') / 'output.txt'
    if not path.exists():
        path.touch()

    # Scrape all fairytales
    for link in tqdm(links):

        # Download the fairytale and extract the text, using the `newspaper3k`
        # library
        article = Article(link)
        article.download()
        article.parse()
        doc = article.text

        # Remove numbers, and split into sentences
        doc = re.sub('["0-9]', '', doc)
        doc = re.sub('! *', '!\n', doc)
        doc = re.sub(r'[:;.] *', '.\n', doc)

        # Remove duplicate line breaks
        doc = re.sub('\n+', '\n', doc)

        # Split into lines, and ensure that the lines has between 4 and 14
        # words, as that's the requirement by CommonVoice. Altså ensure that
        # the sentences are in title case
        lines = [line.title() for line in doc.split('\n')
                      if len(line.split()) >= 4 and len(line.split()) < 14]

        # Filter the lines further by removing all the sentences starting with
        # 'sagde' and 'råbte', and removing sentences which are just symbols
        lines = [line for line in lines
                      if len(re.sub('[^a-z]', '', line)) > 0 and
                         not line.lower().startswith('sagde') and
                         not line.lower().startswith('råbte')]

        # Join all the sentences into one long string
        doc = '\n'.join(lines)

        # Append the string to the output file
        with path.open('a') as f:
            f.write(doc + '\n')


if __name__ == '__main__':
    scrape_andersen()
