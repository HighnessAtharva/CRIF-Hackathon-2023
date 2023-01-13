



# def get_headline(content):
#     r = requests.get(content)
#     soup = BeautifulSoup(r.content, "html.parser")
#     return soup.find('h1').get_text()


# def sentiment_score_to_summary(sentiment_score: int) -> str:
#         """
#         Converts the sentiment score to a summary
#         Args:
#             sentiment_score (int): sentiment score
#         Returns:
#             str: summary of the sentiment score
#         """
#         if sentiment_score == 1:
#             return "Extremely Negative"
#         elif sentiment_score == 2:
#             return "Somewhat Negative"
#         elif sentiment_score == 3:
#             return "Generally Neutral"
#         elif sentiment_score == 4:
#             return "Somewhat Positive"
#         elif sentiment_score == 5:
#             return "Extremely Positive"
        
        
# def sentiment_analysis(content: str) -> None:
#     """
#     Performs sentiment analysis on the text and prints the sentiment score and the summary of the score
#     Args:
#         content (str): text/url to be analyzed
#     """
#     tokenizer = AutoTokenizer.from_pretrained(
#         "nlptown/bert-base-multilingual-uncased-sentiment")
#     model = AutoModelForSequenceClassification.from_pretrained(
#         "nlptown/bert-base-multilingual-uncased-sentiment")
#     tokens = tokenizer.encode(
#         content, return_tensors='pt', truncation=True, padding=True)
#     result = model(tokens)
#     result.logits
#     sentiment_score = int(torch.argmax(result.logits))+1
#     return sentiment_score_to_summary(sentiment_score)



# # sourcery skip: identity-comprehension
# nlp = spacy.load("en_core_web_trf")

# with open ('negative_words.txt', 'r', encoding='utf-8') as file:
#     negative_words = file.read().splitlines()

# with open ('bad_words.txt', 'r', encoding='utf-8') as file:
#     bad_words = file.read().splitlines()

# with open ('countries.txt', 'r', encoding='utf-8') as file:
#     countries = file.read().splitlines()
    
# with open('lawsuits.txt', 'r', encoding='utf-8') as file:
#     lawsuits = file.read().splitlines()
    
# with open('harassment.txt', 'r', encoding='utf-8') as file:
#     harassment = file.read().splitlines()

# with open(f'.csv', 'w', encoding='latin-1') as summary:
    
#     # read first row from Uber.csv
#     with open('CHECKPOINT1.csv', 'r', encoding='latin-1') as file:
#         try:
#             reader = csv.reader(file)
#             next(reader)
#             # do for every news article
#             for idx, row in enumerate(reader, start=1):
#                 url= row[3]
#                 raw_text = row[4]
                
#                 headline=get_headline(url)
#                 headline_sentiment=sentiment_analysis(headline)
                
#                 negative_words=[]
#                 offensive_words=[]
#                 tags=[]
                
#                 if headline_sentiment in ["Extremely Negative", "Somewhat Negative"]:
#                     offense_rating=0
                    

#                     if headline_sentiment=="Somewhat Negative":
#                         offense_rating+=100
                    
#                     # tag as hate speech
#                     elif headline_sentiment=="Extremely Negative":
#                         offense_rating+=200
                    
#                     nlp_text= nlp(raw_text)

                    
#                     # add custom entities
#                     for word in nlp_text:
#                         # if it is a negative word
#                         if word.text in negative_words:
#                             offense_rating+=10
#                             negative_words.append(word.text)
                            
                            
#                         # if it is a highly offensive word 
#                         elif word.text in bad_words:
#                             offense_rating+=50
#                             offensive_words.append(word.text)
#                             tags.append("hate speech")
    
#                         # if the article is talks about lawsuits
#                         if word.text in lawsuits:
#                             offense_rating+=30
#                             tags.append("lawsuit")
                        
#                         # if the article is about harassment
#                         if word.text in harassment:
#                             offense_rating+=50
#                             tags.append("harassment")
                        
#                         # does article mention a country?
#                         if word.text in countries:
#                             tags.append("country")    
                    
#                         # does article mention a person
#                         if word.ent_type_ == "PERSON":
#                             tags.append(word)     
                                                
                    
#                     if offense_rating>20:
#                         offense_rating-=10


#                     # write to csv
#                     writer = csv.writer(summary)
#                     # Write Column Headers
#                     writer.writerows([["Article", "Headline", "Headline Sentiment", "Offense Rating", "Negative Words", "Offensive Words"]])
                    
#                     # Write each row
#                     writer.writerow([idx, headline, headline_sentiment, offense_rating, [word for word in negative_words], [word for word in offensive_words]])
#                     print(f"Article {idx} written to csv")
                
#         except Exception as e:
#             pass    

           





