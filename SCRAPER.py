import csv
import trafilatura
import re
from newsapi import NewsApiClient
from rich import print
import os
import csv
import spacy
from spacy import displacy
import requests
import torch
import json
from bs4 import BeautifulSoup
from spacy.lang.en.stop_words import STOP_WORDS
from spacytextblob.spacytextblob import SpacyTextBlob
from transformers import AutoModelForSequenceClassification, AutoTokenizer


# =========================
# UTIL FUNCTIONS          #
# =========================
def parse_text_from_web(webURL: str) -> str:
    """Extracts the text from the main content of the web page. Removes the ads, comments, navigation bar, footer, html tags, etc
    Args:
        webURL (str): URL of the web page
    Returns:
        str: clean text from the web page
    Raises:
        trafilatura.errors.FetchingError: If the URL is invalid or the server is down
    """

    try:
        downloaded = trafilatura.fetch_url(webURL)
        article= trafilatura.extract(downloaded, include_comments=False, include_tables=False, with_metadata=False, include_formatting=True, target_language='en', include_images= False)

        return article

    except Exception as e:
        pass

def cleanup_text(text: str) -> str:
    """Clean up the text by removing special characters, numbers, whitespaces, etc for further processing and to improve the accuracy of the model.
    Args:
        text (str): text to be cleaned up
    Returns:
        str: cleaned up text
    """

    # text = re.sub(r'\d+', '', text)  # remove numbers
    
    # text = re.sub(r'\s+', ' ', text)  # remove whitespaces
    try:
        # remove special characters except full stop and apostrophe
        text = re.sub(r'[^a-zA-Z0-9\s.]', '', text)
        
        # text = text.lower()  # convert text to lowercase
        text = text.strip()  # remove leading and trailing whitespaces
        text = text.encode('ascii', 'ignore').decode('ascii')  # remove non-ascii characters

        # split text into words without messing up the punctuation
        text = re.findall(r"[\w']+|[.,!?;]", text)

        text= ' '.join(text)
        return text.replace(' .', '.')
    except Exception as e:
        pass



# =========================
# SCRAPING                #
# =========================
def scrape_news(organization: str) -> list:
    # sourcery skip: inline-immediately-returned-variable
    
    try:
        # newsAPI
        api_key=os.getenv('NEWSAPI')

        newsapi = NewsApiClient(api_key=api_key)

        # get TOP articles, 1st page, grab 25 articles
        all_articles = newsapi.get_everything(q=organization, from_param='2022-12-20', to='2023-01-12', language='en', sort_by='relevancy', page=1, page_size=30)

        return all_articles
    
    except Exception as e:
        pass
        




# =========================
# WRITE TO CSV            #
# =========================
def write_to_csv(organization: str, all_articles: dict) -> None:
    with open(f'CSVs/{organization}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Article", "Title", "Description", "PublishedAt", "URL", "Content"])

        for idx, article in enumerate(all_articles['articles']):
            title= article['title'].strip()
            description= article['description'].strip()
            publishedAt= article['publishedAt']
            newsURL= article['url']
            
            content= parse_text_from_web(newsURL)
            content=cleanup_text(content)
        
            # download the content from the url
            writer.writerow([idx, article['title'], article['description'], article['publishedAt'], article['url'], content])
            
            print(f"[bold]Wrote {idx} -{title} to {organization}.csv[/bold]")
            
        print(f"[bold]Wrote {len(all_articles['articles'])} to {organization}.csv[/bold]")
    
    

# =========================
# SENTIMENT              #
# =========================

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

def sentiment_score_to_summary(sentiment_score: int) -> str:
        """
        Converts the sentiment score to a summary
        Args:
            sentiment_score (int): sentiment score
        Returns:
            str: summary of the sentiment score
        """
        if sentiment_score == 1:
            return "Extremely Negative"
        elif sentiment_score == 2:
            return "Somewhat Negative"
        elif sentiment_score == 3:
            return "Generally Neutral"
        elif sentiment_score == 4:
            return "Somewhat Positive"
        elif sentiment_score == 5:
            return "Extremely Positive"
        
        
def sentiment_analysis(content: str) -> None:
    """
    Performs sentiment analysis on the text and prints the sentiment score and the summary of the score
    Args:
        content (str): text/url to be analyzed
    """
    tokenizer = AutoTokenizer.from_pretrained(
        "nlptown/bert-base-multilingual-uncased-sentiment")
    model = AutoModelForSequenceClassification.from_pretrained(
        "nlptown/bert-base-multilingual-uncased-sentiment")
    tokens = tokenizer.encode(
        content, return_tensors='pt', truncation=True, padding=True)
    result = model(tokens)
    result.logits
    sentiment_score = int(torch.argmax(result.logits))+1
    return sentiment_score_to_summary(sentiment_score)


def process_csv(organization):  # sourcery skip: identity-comprehension

    with open ('negative_words.txt', 'r', encoding='utf-8') as file:
        negative_words_list = file.read().splitlines()

    with open ('bad_words.txt', 'r', encoding='utf-8') as file:
        bad_words = file.read().splitlines()

    with open ('countries.txt', 'r', encoding='utf-8') as file:
        countries = file.read().splitlines()
        
    with open('lawsuits.txt', 'r', encoding='utf-8') as file:
        lawsuits = file.read().splitlines()
        
    with open('harassment.txt', 'r', encoding='utf-8') as file:
        harassment = file.read().splitlines()



    with open(f'CSVs/{organization}-processed.csv', 'w', encoding='utf-8', newline='') as summary:
        
        # read first row from Uber.csv
        with open(f'CSVs/{organization}.csv', 'r', encoding='utf-8') as file:
            try:
                reader = csv.reader(file)
                next(reader)
                
                # write to csv
                writer = csv.writer(summary)
                
                # do for every news article
                writer.writerows([["Article", "Headline", "Headline Sentiment", "Offense Rating", "Negative Words", "Offensive Words", "Tags"]])
                
                for idx, row in enumerate(reader, start=1):
                    url= row[3]
                    raw_text = row[4]
    
                    # parse_text_from_web(webURL)
                    
                    headline=get_headline(url)
                    headline_sentiment=sentiment_analysis(headline)
                    
                    negative_words=[]
                    offensive_words=[]
                    tags=[]
                    
                    
                    offense_rating=0
                    

                    if headline_sentiment=="Somewhat Negative":
                        offense_rating+=100
                    
                    # tag as hate speech
                    elif headline_sentiment=="Extremely Negative":
                        offense_rating+=200
                    
                    nlp_text= nlp(raw_text)

                    
                    # add custom entities
                    for word in nlp_text:
                        # if it is a negative word
                        if word.text.lower() in negative_words_list:
                            offense_rating+=10
                            negative_words.append(word.text)
                            
                            
                        # if it is a highly offensive word 
                        elif word.text.lower() in bad_words:
                            offense_rating+=50
                            offensive_words.append(word.text)
                            
    
                        # if the article is talks about lawsuits
                        if word.text.lower() in lawsuits:
                            offense_rating+=30
                            tags.append("lawsuit")
                        
                        # if the article is about harassment
                        if word.text.lower() in harassment:
                            offense_rating+=50
                            tags.append("harassment")
                        
                        # does article mention a country?
                        if word.text.lower() in countries:
                            tags.append("country")    
                    
                        # does article mention a person
                        if word.ent_type_ == "PERSON":
                            tags.append(word)     
                                                
                    
                    if offense_rating>20:
                        offense_rating-=10
                        
                    
                    # Write each row
                    writer.writerow([idx, headline, headline_sentiment, offense_rating, [word for word in negative_words], [word for word in offensive_words], [tag for tag in tags]])
                    print(f"Article {idx} written to csv")
                    
                else:
                    print(f"Article {idx} is not offensive. SKIPPING...")
                    
                    
            except Exception as e:
                print(e)
                print(e.__class__)
                print(e.__doc__)
                print(e.__traceback__)
                

def visualize(organization):
    raw_text = ''
    with open('CSVs/{organization}.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        
        # do for every news article
        for idx, row in enumerate(reader, start=1):
            raw_text += row[4]
        
        nlp_text = nlp(raw_text)
        displacy.serve(nlp_text, style="ent")

def merge_csv(csv1, csv2, organization):
    import pandas as pd
    df1 = pd.read_csv(csv1)
    df2 = pd.read_csv(csv2) 
    df = pd.merge(df1, df2, on='Article')
    df.to_csv(f'CSVs/{organization}-ANALYSIS.csv', index=False)
    print(f"CSVs merged to {organization}-ANALYSIS.csv")
    
    
# sourcery skip: identity-comprehension
nlp = spacy.load("en_core_web_trf")

import os

# # sourcery skip: inline-immediately-returned-variable
print("[bold green reverse]ENTER AN ORGANIATION NAME TO PERFORM MEDIA ANALYSIS ON[/bold green reverse]")
organization=input()

if os.path.exists(path=f'CSVs/{organization}.csv'):
    print(f"Found {organization}.csv")
    
else:
    articles=scrape_news(organization)
    write_to_csv(organization, articles)


if os.path.exists(path=f'CSVs/{organization}-processed.csv'):
    print(f"Found {organization}-processed.csv")
else:
    process_csv(organization)

file1=f'CSVs/{organization}.csv'
file2=f'CSVs/{organization}-processed.csv'
merge_csv(file1, file2, organization)


