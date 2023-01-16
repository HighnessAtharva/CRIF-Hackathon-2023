# TODO: prevent utf-8 encoding errors in CSVs
# TODO: add a progress bar for all timed processes
# TODO: Maintain History of organizations analyzed
# TODO: Show time taken to scrape and analyze (tock - tick)

#Importing Libraries
import contextlib
import csv
import json
import os
import re
import time
import warnings
from platform import platform, system

import matplotlib.pyplot as plt
import requests
import spacy
import torch
import trafilatura
from bs4 import BeautifulSoup
from newsapi import NewsApiClient
from rich import box, print
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.progress import track
from rich.syntax import Syntax
from rich.text import Text
from spacy import displacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacytextblob.spacytextblob import SpacyTextBlob
from transformers import AutoModelForSequenceClassification, AutoTokenizer

warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd


# =========================#
# UTIL FUNCTIONS           #
# =========================#
def parse_text_from_web(webURL: str) -> str:
    """Extracts the text from the main content of the web page. Removes the ads, comments, navigation bar, footer, html tags, etc
    Args:
        webURL (str): URL of the web page
    Returns:
        str: clean text from the web page
    Raises:
        trafilatura.errors.FetchingError: If the URL is invalid or the server is down
    """

    with contextlib.suppress(Exception):
        downloaded = trafilatura.fetch_url(webURL)
        return trafilatura.extract(
            downloaded,
            include_comments=False,
            include_tables=False,
            with_metadata=False,
            include_formatting=True,
            target_language='en',
            include_images=False,
        )

# =========================#
# cleanup FUNCTIONS        #
# =========================#
def cleanup_text(text: str) -> str:
    """Clean up the text by removing special characters, numbers, whitespaces, etc for further processing and to improve the accuracy of the model.
    Args:
        text (str): text to be cleaned up
    Returns:
        str: cleaned up text
    """

    # text = re.sub(r'\d+', '', text)  # remove numbers

    # text = re.sub(r'\s+', ' ', text)  # remove whitespaces
    with contextlib.suppress(Exception):
        # remove special characters except full stop and apostrophe
        text = re.sub(r'[^a-zA-Z0-9\s.]', '', text)

        # text = text.lower()  # convert text to lowercase
        text = text.strip()  # remove leading and trailing whitespaces
        text = text.encode('ascii', 'ignore').decode('ascii')  # remove non-ascii characters

        # split text into words without messing up the punctuation
        text = re.findall(r"[\w']+|[.,!?;]", text)
    
        text= ' '.join(text)
        return text.replace(' .', '.')



# ========================#
# SCRAPING                #
# ========================#
def scrape_news(organization: str) -> list:
    # sourcery skip: inline-immediately-returned-variable, use-contextlib-suppress
    
    try:
        # newsAPI
        api_key=os.getenv('NEWSAPI')

        newsapi = NewsApiClient(api_key=api_key)

        # get TOP articles, 1st page, grab 3 articles
        all_articles = newsapi.get_everything(q=organization, from_param='2022-12-20', to='2023-01-12', language='en', sort_by='relevancy', page=1, page_size=10)

        return all_articles
    
    except Exception as e:
        pass
        




# ========================#
# WRITE TO CSV            #
# ========================#
def write_to_csv(organization: str, all_articles: dict) -> None:
    with open('CSVs/COMMON.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Article", "Title", "Description",  "URL", "Content", "Published"])
        for idx, article in enumerate(all_articles['articles'], start=1):
            title= article['title'].strip()
            description= article['description'].strip()
            publishedAt= article['publishedAt']
            newsURL= article['url']

            content= parse_text_from_web(newsURL)
            content= cleanup_text(content)

            # download the content from the url
            writer.writerow([idx, article['title'], article['description'], article['url'], content, publishedAt])

            print(f"✅ [bold green]SUCCESS! Wrote {idx} - [bold blue]{title}[/bold blue] to [gold1]{organization}[/gold1].csv")

        # Adding the parsed content to the CSV    
        print(f"[bold green]DONE! WROTE {len(all_articles['articles'])} ARTICLES TO [r]COMMON.csv[/r][/bold green]")
    
    

# ========================#
# SENTIMENT scoring       #
# ========================#

#egt the headlines
def get_headline(content, organization):
    r = requests.get(content)
    #parse the text
    soup = BeautifulSoup(r.content, "html.parser")
    if soup.find('h1'):
        headline=soup.find('h1').get_text()
        if len(headline.split())<=2:
            headline="No Headline"
    
    else:
        headline="No Headline"
        
    # TODO: HANDLE IMPROVISATION OF HEADERS LATER
                
    
        
    
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
        
#calculate the sentiment score       
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

# sourcery skip: identity-comprehension
def process_csv(organization):  

    with open ('word-store/negative_words.txt', 'r', encoding='utf-8') as file:
        negative_words_list = file.read().splitlines()

    with open ('word-store/bad_words.txt', 'r', encoding='utf-8') as file:
        bad_words = file.read().splitlines()

    with open ('word-store/countries.txt', 'r', encoding='utf-8') as file:
        countries = file.read().splitlines()

    with open('word-store/lawsuits.txt', 'r', encoding='utf-8') as file:
        lawsuits = file.read().splitlines()

    with open('word-store/harassment.txt', 'r', encoding='utf-8') as file:
        harassment = file.read().splitlines()



# ========================#
# Creating Final csv      #
# ========================#
    #definig charset
    with open('CSVs/COMMON-PROCESSED.csv', 'w', encoding='utf-8', newline='') as summary:
        
        # read first row from Uber.csv
        with open('CSVs/COMMON.csv', 'r', encoding='utf-8') as file:
            try:
                reader = csv.reader(file)
                next(reader)

                # write to csv
                writer = csv.writer(summary)

                # do for every news article
                writer.writerows([["Article", "Headline", "Headline Sentiment", "Offense Rating", "Negative Words", "Offensive Words", "Tags"]])

                print("[bold gold1]===============================[/bold gold1]\n\n")
                for idx, row in enumerate(reader, start=1):
                    url= row[3]
                    raw_text = row[4]

                    # parse_text_from_web(webURL)

                    headline=get_headline(url, organization)
                    headline_sentiment=sentiment_analysis(headline)

                    negative_words=[]
                    offensive_words=[]
                    tags=[]

                    # init ofense rating
                    offense_rating=0

                    # tag as negative
                    if headline_sentiment == "Extremely Negative":
                        offense_rating+=200

                    elif headline_sentiment == "Somewhat Negative":
                        offense_rating+=100

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
                    writer.writerow(
                        [
                            idx,
                            headline,
                            headline_sentiment,
                            offense_rating,
                            list(negative_words),
                            list(offensive_words),
                            list(tags),
                        ]
                    )
                    print(f"Article {idx} written to csv")

                print(f"✔ [bold u r]\nSUCCESS! Finished processing COMMON-PROCESSED.csv[/bold u r]")


            except Exception as e:
                print(e)
                print(e.__class__)
                print(e.__doc__)
                print(e.__traceback__)
                
# ========================#
# Display temp output     #
# ========================#

#visualize the text in html
def visualize(organization):
    raw_text = ''
    with open('CSVs/COMMON.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)

        # do for every news article
        for idx, row in enumerate(reader, start=1):
            raw_text += row[4]

        nlp_text = nlp(raw_text)

        print("\n🚀 [bold magenta r]NER COMPLETE, all words tagged...[/bold magenta r]")
        # serve the displacy visualizer
        displacy.serve(nlp_text, style="ent")

# ========================#
# Merging Raw data        #
# ========================#

def merge_csv(csv1, csv2, organization):
    
    df1 = pd.read_csv(csv1, encoding='unicode_escape')
    df2 = pd.read_csv(csv2, encoding='unicode_escape')
    df = pd.merge(df1, df2, on='Article')
    import random

    num=random.randint(1, 100)

    # # check if COMMON-ANALYSIS exists then copy and rename it to COMMON-ANALYSIS-1
    # if os.path.exists('CSVs/COMMON-ANALYSIS.csv'):
    #     os.rename('CSVs/COMMON-ANALYSIS.csv', f'CSVs/COMMON-ANALYSIS-{num}.csv')

    df.to_csv('CSVs/COMMON-ANALYSIS.csv', index=False)
    print("CSVs merged to COMMON-ANALYSIS.csv")
    

      
# ========================#
# cleaing up -2           #
# ========================#   
# RUN SAME FUNCTION TWICE 
def final_cleanup(organization):
    
    df = pd.read_csv('CSVs/COMMON-ANALYSIS.csv', encoding='unicode_escape')
    

    # write - to empty cells in offensive words
    df['Offensive Words'] = df['Offensive Words'].fillna('-')
    
    # write - to empty cells in negative words 
    df['Negative Words'] = df['Negative Words'].fillna('-')
     
    # write - to empty cells in tags
    df['Tags'] = df['Tags'].fillna('-')
    
    # clean up tags
    df['Tags'] = df['Tags'].str.replace('[', '').str.replace(']', '').str.replace("'", '')
    
    # clean up offensive words
    df['Offensive Words'] = df['Offensive Words'].str.replace('[', '').str.replace(']', '').str.replace("'", '')
    
    # clean up negative words
    df['Negative Words'] = df['Negative Words'].str.replace('[', '').str.replace(']', '').str.replace("'", '')
    
    df.to_csv('CSVs/COMMON-ANALYSIS.csv', index=False)
#get orgainizations url   
def get_sub_url(organization):
    
    with open ('CSVs/COMMON-ANALYSIS.csv', 'r', encoding='utf-8') as f:
        with open ('CSVs/COMMON-ANALYSIS.csv', 'w', encoding='utf-8') as f2:
            publisher=[]
            reader = csv.reader(f)
            url = [row[4] for row in reader]
            # remove www. and https:// from url
            url = [re.sub(r'www.', '', i) for i in url]
            url = [re.sub(r'https://', '', i) for i in url]
            for x in url:
                name= x.split('.com/')[0]
                publisher.append(name)
                    
            # replace items from publisher where character length is more than 40 with '-'
            publisher = [re.sub(r'.{40,}', '-', i) for i in publisher]         
            print(publisher)
    print("CSVs cleaned up to COMMON-ANALYSIS.csv")   
# sourcery skip: identity-comprehension
nlp = spacy.load("en_core_web_trf")



# ========================#
# Console Output          #
# ========================#

# no tests for this function as it is not called anywhere in the command directly
def get_terminal_width() -> int:
    """
    Gets the width of the terminal.
    Returns: 
        int: width of the terminal.
    """
    try:
        width, _ = os.get_terminal_size()
    except OSError:
        width = 80

    if system().lower() == "windows":
        width -= 1

    return width



def print_banner(console) -> None:
    """
    Prints the banner of the application.
    Args:
        console (Console): Rich console object.
    """

    banner = """
::::    ::::  :::::::::: ::::::::: :::::::::::     :::              :::     ::::    :::     :::     :::     :::   :::  :::::::: ::::::::::: ::::::::  
+:+:+: :+:+:+ :+:        :+:    :+:    :+:       :+: :+:          :+: :+:   :+:+:   :+:   :+: :+:   :+:     :+:   :+: :+:    :+:    :+:    :+:    :+: 
+:+ +:+:+ +:+ +:+        +:+    +:+    +:+      +:+   +:+        +:+   +:+  :+:+:+  +:+  +:+   +:+  +:+      +:+ +:+  +:+           +:+    +:+        
+#+  +:+  +#+ +#++:++#   +#+    +:+    +#+     +#++:++#++:      +#++:++#++: +#+ +:+ +#+ +#++:++#++: +#+       +#++:   +#++:++#++    +#+    +#++:++#++ 
+#+       +#+ +#+        +#+    +#+    +#+     +#+     +#+      +#+     +#+ +#+  +#+#+# +#+     +#+ +#+        +#+           +#+    +#+           +#+ 
#+#       #+# #+#        #+#    #+#    #+#     #+#     #+#      #+#     #+# #+#   #+#+# #+#     #+# #+#        #+#    #+#    #+#    #+#    #+#    #+# 
###       ### ########## ######### ########### ###     ###      ###     ### ###    #### ###     ### ########## ###     ######## ########### ########  
            """
    width = get_terminal_width()
    height = 10
    # defining the panel
    panel = Panel(
        Align(
            Text(banner, style="green"),
            vertical="middle",
            align="center",
        ),
        width=width,
        height=height,
        subtitle="[bold blue]Built for CRIF Hackathon 2023![/bold blue]",
    )
    console.print(panel)


    
# ========================#
# Call of funtions        #
# ========================#

#start cli
console = Console(record=False, color_system="truecolor")
print_banner(console)

# sourcery skip: inline-immediately-returned-variable

# ========================#
print(Panel.fit("[bold green reverse]ENTER AN ORGANIZATION NAME TO PERFORM MEDIA ANALYSIS ON[/bold green reverse]"))
organization=input()

articles=scrape_news(organization)
write_to_csv(organization, articles)
process_csv(organization)

file1='CSVs/COMMON.csv'
file2='CSVs/COMMON-processed.csv'
merge_csv(file1, file2, organization)

final_cleanup(organization)
final_cleanup(organization)

# get_sub_url(organization)
print(Panel.fit("[bold green reverse]ANALYSIS COMPLETE.[/bold green reverse]\nNow performing Named Entity Recognition on the articles and preparing a visualization."))
visualize(organization)




