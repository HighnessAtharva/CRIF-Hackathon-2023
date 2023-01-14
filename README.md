# CRIF-Hackathon-2023

Media Analytics with News Downloader, NER Module to extract risk/threatening statements based on Input company with a Tableau dashboard

## Problem Statement

**Media Analytics**

**Detailed Statement**: Build a framework/utility that takes a company name as an input. The utility should search all the media articles about the input company and present any reputational threatening data on a concise dashboard.

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

