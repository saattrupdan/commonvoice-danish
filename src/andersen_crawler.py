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

    # Create the output file and make sure that it's empty
    path = Path('data') / 'output.txt'
    if path.exists():
        path.unlink()
    path.touch()

    # Scrape all fairytales
    for link in tqdm(links, desc='Scraping fairytales'):

        # Download the fairytale and extract the text, using the `newspaper3k`
        # library
        article = Article(link)
        article.download()
        article.parse()
        doc = article.text

        # Remove numbers, and split into sentences
        doc = re.sub(r'[^a-zA-Z\æ\ø\å\Æ\Ø\Å\-,.:;! ]', '', doc.lower())
        doc = re.sub(r'[:;.!] *', '.\n', doc)

        # Remove duplicate line breaks and whitespace
        doc = re.sub('\n+', '\n', doc)
        doc = re.sub(' +', ' ', doc)

        # Strip the lines and make sure that the first letter is capitalised
        lines = [line.strip('\-,.:;! ').capitalize()
                 for line in doc.split('\n')]

        # Filter the lines
        lines = [line for line in lines
                      if len(re.sub('[^a-z]', '', line)) > 0 and
                         not line.lower().startswith('sagde') and
                         not line.lower().startswith('tænkte') and
                         not line.lower().startswith('råbte') and
                         len(line.split()) >= 4 and
                         len(line.split()) < 14]

        # Join all the sentences into one long string
        doc = '\n'.join(lines)

        # Append the string to the output file
        with path.open('a') as f:
            f.write(doc + '\n')


if __name__ == '__main__':
    scrape_andersen()
