import csv
import spacy
from spacy import displacy
# from transformers import AutoTokenizer, AutoModelForTokenClassification
# from transformers import pipeline
# tokenizer = AutoTokenizer.from_pretrained("dslim/bert-base-NER")
# model = AutoModelForTokenClassification.from_pretrained("dslim/bert-base-NER")
# NER = pipeline("ner", model=model, tokenizer=tokenizer)

nlp = spacy.load("en_core_web_trf")

# get negative/offensive words (racist, sexist, loss, negative reviews, etc.)
with open ('negative_words.txt', 'r', encoding='utf-8') as file:
    negative_words = file.read().splitlines()

with open ('bad_words.txt', 'r', encoding='utf-8') as file:
    bad_words = file.read().splitlines()



# read first row from Uber.csv
with open('Uber.csv', 'r', encoding='latin-1') as file:
    reader = csv.reader(file)
    next(reader)
    # do for every news article
    for idx, row in enumerate(reader, start=1):
        raw_text = row[4]
        
        
            
        nlp_text= nlp(raw_text)
        ner={}
        
        # print only org and product entities
        for word in nlp_text.ents:
            if word.label_ in ["ORG", "PRODUCT", "PERSON"] and word.text not in ner:
                ner[word.text]= word.label_

        # add custom entities
        for word in nlp_text:
            if word.text in negative_words:
                ner[word.text]= "NEGATIVE"
            if word.text in bad_words:
                ner[word.text]= "OFFENSIVE"

        print(f"==============ARTICLE {idx} START==============")
        print(ner)
        print(f"==============ARTICLE {idx} FINISH==============")
        





# show visualization
displacy.serve(nlp_text, style="ent")




