import csv
import trafilatura
import re
from newsapi import NewsApiClient
from rich import print
import os

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

    downloaded = trafilatura.fetch_url(webURL)
    return trafilatura.extract(downloaded, include_comments=False, include_tables=False, with_metadata=False, include_formatting=True, target_language='en', include_images= False)


def cleanup_text(text: str) -> str:
    """Clean up the text by removing special characters, numbers, whitespaces, etc for further processing and to improve the accuracy of the model.
    Args:
        text (str): text to be cleaned up
    Returns:
        str: cleaned up text
    """

    text = re.sub("\xc2\xa0", "", text)  # Deal with some weird tokens
    text = re.sub(r'\d+', '', text)  # remove numbers
    text = re.sub(r'\s+', ' ', text)  # remove whitespaces
    # remove special characters except full stop and apostrophe
    text = re.sub(r'[^a-zA-Z0-9\s.]', '', text)
    # text = text.lower()  # convert text to lowercase
    text = text.strip()  # remove leading and trailing whitespaces
    text = text.encode('ascii', 'ignore').decode('ascii')  # remove non-ascii characters

    # split text into words without messing up the punctuation
    text = re.findall(r"[\w']+|[.,!?;]", text)

    text= ' '.join(text)
    return text.replace(' .', '.')




# =========================
# SCRAPING                #
# =========================

print("[bold green reverse]ENTER AN ORGANIATION NAME TO PERFORM MEDIA ANALYSIS ON[/bold green reverse]")
organization=input()

# newsAPI
api_key=os.getenv('NEWSAPI')

newsapi = NewsApiClient(api_key=api_key)

# get TOP articles, 1st page, grab 25 articles
all_articles = newsapi.get_everything(q=organization, from_param='2022-12-20', to='2023-01-12', language='en', sort_by='relevancy', page=1, page_size=30)



# =========================
# WRITE TO CSV            #
# =========================
with open(f'{organization}.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Title", "Description", "PublishedAt", "URL", "Content"])

        for article in all_articles['articles']:
            title= article['title'].strip()
            description= article['description'].strip()
            publishedAt= article['publishedAt']
            newsURL= article['url']
            
            content= parse_text_from_web(newsURL)
            content=cleanup_text(content)
           
            # download the content from the url
            writer.writerow([article['title'], article['description'], article['publishedAt'], article['url'], content])
            
            
print(f"[bold]Wrote {len(all_articles['articles'])} to articles.csv[/bold]")
    
    

    
    