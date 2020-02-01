from bs4 import BeautifulSoup
import requests, re, html2text

class SourceFetcher:
    def __init__(self, parse_function):
        self.parse_function = parse_function
        self.history = self.get_all_items()

    def get_all_items(self):
        return self.parse_function()[::-1]
    
    def get_new_items(self):
        result = []
        for item in self.get_all_items():
            if item not in self.history:
                self.history.append(item)
                result.append(item)
        return result
    
    def get_history(self):
        return self.history
    
    def get_last(self):
        print(len(self.history))
        if len(self.history) > 0:
            return self.history[-1]

def parse_source_1():
    url = 'https://www.merkur.de/welt/coronavirus-deutschland-merkel-china-bayern-was-ist-symptome-infektion-news-muenchen-zr-13500123.html'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    article_html = soup.find(id='id-js-DocumentDetail').prettify(formatter="html")
    md = html2text.html2text(article_html)

    md = md.split('\n\n')
    results = []
    ree = re.compile(r'\*\*.+[\d\.]+ Uhr:\*\* .+')
    for part in md:
        part = part.replace('\n', ' ')
        if ree.match(part):
            if part not in results:
                results.append(part)
    return results

def parse_source_2():
    url = 'https://www.merkur.de/welt/coronavirus-gegenmittel-heilung-china-symptome-deutschland-krankheit-australien-homoeopathie-zr-13507549.html'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    article_html = soup.find(id='id-js-DocumentDetail').prettify(formatter="html")
    md = html2text.html2text(article_html)

    md = md.split('\n\n')
    results = []
    ree = re.compile(r'\*\*[\w\d\.\, \:]+\*\* .+')
    for part in md:
        part = part.replace('\n', ' ')
        if ree.match(part):
            if part not in results:
                results.append(part)
    return results

def parse_source_3():
    url = 'https://www.merkur.de/welt/coronavirus-deutsche-aus-wuhan-auf-rueckflug-zr-13451287.html'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    article_html = soup.find(id='id-js-DocumentDetail').prettify(formatter="html")
    md = html2text.html2text(article_html)

    md = md.split('\n\n')
    results = []
    ree = re.compile(r'\*\*[\w\d\.\, \:]+\*\* .+')
    for part in md:
        part = part.replace('\n', ' ')
        if ree.match(part):
            if part not in results:
                results.append(part)
    return results