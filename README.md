# CRIF-Hackathon-2023



## Problem Statement

### Media Analytics

Build a framework/utility that takes a company name as an input. The utility should search all the media articles about the input company and present any reputational threatening data on a concise dashboard.

Following are the functionalities that need to be achieved in order to build a complete solution -

1. **Downloader** -
Download news articles using company name from search engines (Google, Yahoo, Duckduckgo) - Selenium, News API

2. **NER module** -
Named Entity Recognition (Organization + Risk Entity) - Out of the box Spacy NLP models / Taxonomy searches

3. **Relationship module** -
Analyse the articles and carve out sentences(context) where reputation risk elements and company names are present.
Can use dependency parsing or predicate classifiers to establish relationships between risk elements and company names

4. **Dashboard** -
Display these relationships in an appropriate Dashboard => PowerBI / Tableau



## Team

1. Atharva Shah (Yours Truly) - Implementation of the first three modules leveraging NLP, Text Processing, Web Scraping and Debugging. In-charge of leading the team and making the presentation in the final round

2. Gurjas Gandhi - Administration, Mangement, Insightful Feedback

3. Ali Asger Saifee - Problem Solving, Curating Word Lists and Generating Tableau Dashboards

4. Aditya Patil - Documentation, Testing and and Generating Tableau Dashboards

   

## Work

Since the project heavily relies on Web Scraping, Text Processing, NLP and Data Analysis using Python was an obvious choice for it. 

Having prior experience with BeautifulSoup, APIs and Spacy for NLP I immidiately got to work and got the first two modules up and running within the first few hours of the hackathon. 

**NewsAPI** - Scraping the latest and relevant news about an organization based on the input query 

**Regex, BeautifulSoup, Trifulatura** - To parse the main content from the webpages and discard irrelevant data. Cleaning up news articles. 

**Tensorflow** - Sentiment Analysis (returning a logit score between 1 to 5)

**Spacy** - pre-trained roBERta model for improving sentiment analysis and and tagging of Named Entity Relationships

**Custom Word Stores** - to employ a "weighted list" score system based on the word count of negative and offensive words. Three other lists (harassment.txt, countries.txt, lawsuits.txt) were used to tag the articles if repeated words related to it were detected. 

**Processing CSVs** - A lot of file handling was performed. The pipeline consisted of 3 CSVs.

1. `Common.csv` that simply stores the scraped articles
2. `Common-processed.csv` that performs sentiment analysis on headline and stores the tags, offensive/negative words with the score based on the SpaCy NER module
3. `Common-Analysis.csv` that used pandas to join all the fields together and prepare a final CSV for automating the Tableau dashboard.

Spent the most time with this. Most CSVs that made the final 

**Tableau** - Taking input of the `COMMON-ANALYSIS.csv` file, we designed 8 dashboards to present or narrate a story with all our data. Since we had plenty of fields like `Article Count`, `Title`,` Description`, `Content` (which holds the entire article text), `URL`, `Publisher`, `Published Date`, `Headline`, `Headline Sentiment`, `Offensive Rating`, `Negative Words`, `Offensive Words and Tags` it was not much of a hassle. We made good use of several plotting and graphing methods and presented a diverse yet insightful story. Each Tableau report updates after looking up a new organization.  



### Obstacles, Setbacks and Challenges faced

- Cleaning up the article body and parsing proper text.

- Extrapolating the context to base the negative score on.

- Optimizing NLP processing and reducing the scraping time. 

- Tableau was a completely new tool for us, nonetheless we took a 2 hour crash course and got our hands dirty thanks to which we could quickly get ahead of the game and visualize our gathered data seamlessly.

- Handling exceptions, 403, 404, Date Parsing, Tagging and taking care of API throttling. 

- Module 3 felt to be the most challenging since we had to add our own "risk-entity" NER support to the SpaCy "roBERTa" model while also not losing application efficiency. 

  

## Rewards

We worked around the clock in an organized manner and secured the first rank competing against 36 other teams (nearly 140+ participants). All the effort paid off at the end as we secured the first position after an exhaustive and interview-based project presentation with the panel of judges. 

With the prestige and recognition we also recieved:-

- 50K Cash Prize
- Goodies for each team member
- Victory Certificate for each team member
- A "winner takes it all" trophy



