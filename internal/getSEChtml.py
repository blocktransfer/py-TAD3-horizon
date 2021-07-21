from bs4 import BeautifulSoup
import requests
from pprint import pprint

data = requests.get("https://www.sec.gov/Archives/edgar/data/1616262/000143774919024779/rmcfd20191222_defa14a.htm", {"User-Agent": "John Wooten john@blocktransfer.io", "Accept-Encoding": "deflate", "Host": "www.sec.gov"}).text

pprint(BeautifulSoup(data, 'html.parser'))


