## Description: Visualize the named entities in the news articles
#import libraries
import csv
import spacy
from spacy import displacy
#load the model
nlp = spacy.load("en_core_web_trf")
#function to visualize the named entities
def visualize(organization):
    raw_text = ''
    with open(f'CSVs/{organization}.csv', 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        next(reader)
        
        # do for every news article
        for idx, row in enumerate(reader, start=1):
            raw_text += row[4]
        
        nlp_text = nlp(raw_text)
        displacy.serve(nlp_text, style="ent")
        
        
#call the function
visualize('pitchfork')