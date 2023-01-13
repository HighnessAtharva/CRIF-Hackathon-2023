from bs4 import BeautifulSoup
import requests

url="https://beebom.com/lenovo-tab-p11-5g-launched-india/"

def get_headline(content):
    r = requests.get(content)
    soup = BeautifulSoup(r.content, "html.parser")
    if soup.find('h1'):
        headline=soup.find('h1').get_text()
        if len(headline.split())<=2:
            headline="No Headline"
                
    else:
        headline="No Headline"
    return headline

get_headline(url)