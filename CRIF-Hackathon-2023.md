# CRIF Hackathon 2023 — Archive Note
### *A project retrospective written from 2026, looking back at an idea we had three years ago*

---

> **tl;dr** — We built a fully automated, NLP-powered media reputation surveillance engine that scraped the internet for news about any company, scored every article for reputational risk, tagged it with custom NER labels, and served the results on an auto-refreshing Tableau dashboard. We entered a hackathon with 36 other teams (140+ participants), ran on no sleep, and walked away with **first place** and a ₹50,000 cash prize.

---

## Table of Contents

1. [Context & Background](#1-context--background)
2. [The Problem Statement](#2-the-problem-statement)
3. [The Team](#3-the-team)
4. [Solution Architecture — The Four Modules](#4-solution-architecture--the-four-modules)
   - [Module 1 — Downloader / Scraper](#module-1--downloader--scraper)
   - [Module 2 — NER Module](#module-2--ner-module)
   - [Module 3 — Relationship & Scoring Module](#module-3--relationship--scoring-module)
   - [Module 4 — Dashboard (Tableau)](#module-4--dashboard-tableau)
5. [The Data Pipeline in Detail](#5-the-data-pipeline-in-detail)
6. [Word Stores — The "Weighted List" System](#6-word-stores--the-weighted-list-system)
7. [The Tech Stack](#7-the-tech-stack)
8. [The Code — SCRAPER.py Walkthrough](#8-the-code--scraperpy-walkthrough)
9. [Companies Analysed](#9-companies-analysed)
10. [Obstacles, Setbacks, and War Stories](#10-obstacles-setbacks-and-war-stories)
11. [Results & Rewards](#11-results--rewards)
12. [Retrospective from 2026](#12-retrospective-from-2026)
13. [Repository Structure](#13-repository-structure)
14. [Original README (preserved verbatim)](#14-original-readme-preserved-verbatim)

---

## 1. Context & Background

**CRIF** is a global data and analytics company headquartered in Bologna, Italy. They are best known for credit risk management, business information, and fraud prevention services — essentially the kind of company that decides whether you get a loan, whether a vendor is creditworthy, or whether a counterparty poses a risk to your business. One of their fast-growing interest areas back in 2023 was *non-financial risk*, specifically: **reputational risk derived from media coverage**.

The idea is simple but powerful. If a company is getting hammered in the news — lawsuits, harassment scandals, regulatory actions, controversies — that is a leading indicator of financial trouble, supply chain disruption, or counterparty default risk. Banks, hedge funds, insurance companies, and procurement teams all want to know: *"Is this company in the news for bad reasons right now?"* Manual media monitoring is slow, expensive, and unscalable. Automated media analytics — that was the gap CRIF wanted to explore.

They ran an internal/partner hackathon in January 2023 with the theme *"Media Analytics for Reputation Risk"* and invited teams of students and young developers to build a proof-of-concept. We were one of those teams.

---

## 2. The Problem Statement

> **Build a framework/utility that takes a company name as input. The utility should search all media articles about the input company and present any reputational-threatening data on a concise dashboard.**

The four functional modules they specified:

| # | Module | What it had to do |
|---|--------|-------------------|
| 1 | **Downloader** | Fetch news articles using the company name from search engines (Google, Yahoo, DuckDuckGo) via Selenium or a News API |
| 2 | **NER Module** | Named Entity Recognition — identify Organisation entities and Risk Entities using out-of-the-box SpaCy NLP models or taxonomy searches |
| 3 | **Relationship Module** | Carve out sentences/contexts where reputation risk elements and company names co-occur; use dependency parsing or predicate classifiers to establish relationships |
| 4 | **Dashboard** | Display the relationships in a PowerBI or Tableau dashboard |

That was the brief. A 4-module pipeline from raw web to visual insight, built in a hackathon window.

---

## 3. The Team

We were a team of four, each bringing a different strength to the table:

| Member | Role & Contribution |
|--------|---------------------|
| **Atharva Shah** *(yours truly)* | Lead developer. Implemented all three NLP/scraping/processing modules. Led the team, directed the technical architecture, and presented the solution to the judging panel in the final round. |
| **Gurjas Gandhi** | Administration and management. Kept the project on track, provided insightful feedback throughout, and was instrumental in generating the Tableau dashboards. |
| **Ali Asger Saifee** | Problem solving and data curation. Built and curated the custom word lists (negative, offensive, harassment, lawsuits, countries) that powered the weighted scoring system. Also helped with Tableau dashboards. |
| **Aditya Patil** | Documentation, testing, and Tableau dashboard generation. Kept the data stories coherent and ensured quality across all 8 visualization sheets. |

---

## 4. Solution Architecture — The Four Modules

### Module 1 — Downloader / Scraper

The entry point of the entire pipeline. Given a company name (e.g., `"Tesla"`), the scraper:

1. **Queries NewsAPI** (`newsapi-python` client) for everything published about the company between a fixed date window (Dec 20, 2022 → Jan 12, 2023 for the demo dataset). Returns up to 10 results per page sorted by relevancy.
2. **Fetches full article content** from each article URL using `trafilatura` — a content-extraction library that strips away navigation bars, ads, comments, sidebars, and HTML cruft, returning only the main body text.
3. **Cleans up the text** with a custom `cleanup_text()` function using regex: removes non-ASCII characters, normalises whitespace, strips special characters while preserving sentence-ending punctuation.
4. **Writes to `COMMON.csv`** with columns: `Article`, `Title`, `Description`, `URL`, `Content`, `Published`.

At this stage we had clean, full-text news articles in a structured CSV. No fluff, no HTML.

```
COMMON.csv
┌─────────┬──────────────────────────────┬──────────────┬─────────────────────┬───────────────┬─────────────────────┐
│ Article │ Title                        │ Description  │ URL                 │ Content       │ Published           │
├─────────┼──────────────────────────────┼──────────────┼─────────────────────┼───────────────┼─────────────────────┤
│ 1       │ Elon Musk isn't serious...   │ ...          │ https://theverge... │ Full article  │ 2022-12-21T01:57:28Z│
│ ...     │ ...                          │ ...          │ ...                 │ ...           │ ...                 │
└─────────┴──────────────────────────────┴──────────────┴─────────────────────┴───────────────┴─────────────────────┘
```

---

### Module 2 — NER Module

**SpaCy** was the NLP backbone. We loaded `en_core_web_trf` — SpaCy's transformer-based (roBERTa) English model — for high-accuracy Named Entity Recognition.

The NER module:
- Processed the full article text through the SpaCy pipeline.
- Identified **PERSON** entities (executives, politicians, public figures mentioned in connection with the company).
- Would eventually feed into the relationship module to understand *who* was being mentioned alongside *which* risk signals.

For visual debugging and demonstration purposes, the `visualize()` function rendered all tagged entities using SpaCy's `displacy.serve()` — an interactive browser-based NER visualizer that highlighted every entity type in the article corpus in colour.

![Module 1 - Scraping](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module1.png)
![Module 2 - NER](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module2.png)
![Module 3 - Scoring](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module3.png)

---

### Module 3 — Relationship & Scoring Module

This was the most intellectually challenging module and the one we spent the most time on. The goal was to produce a quantified *reputation risk score* for each article, together with human-readable metadata about *why* the score is what it is.

**Sentiment Analysis (Headline Level):**
We used `nlptown/bert-base-multilingual-uncased-sentiment` — a fine-tuned BERT model from Hugging Face — to produce a 1–5 star sentiment score on the article headline. The mapping:

| Score | Label |
|-------|-------|
| 1 | Extremely Negative |
| 2 | Somewhat Negative |
| 3 | Generally Neutral |
| 4 | Somewhat Positive |
| 5 | Extremely Positive |

Headlines scoring "Extremely Negative" contributed **+200** to the article's `offense_rating`. "Somewhat Negative" contributed **+100**.

**Word-Level Scoring (Body Text):**
Each word in the full article body was checked against four custom word lists:

| Word List | Match Bonus | What it flags |
|-----------|-------------|---------------|
| `negative_words.txt` | +10 per match | Broadly negative/pessimistic vocabulary |
| `bad_words.txt` | +50 per match | Profanity, slurs, explicit harmful content |
| `lawsuits.txt` | +30 per match | Legal/judicial terminology |
| `harassment.txt` | +50 per match | Discrimination, layoffs, misconduct |

**Tag Generation:**
Beyond the numeric score, each article was tagged for:
- **`lawsuit`** — if lawsuit-related words appeared
- **`harassment`** — if harassment-related words appeared
- **`country`** — if any country name from `countries.txt` appeared (suggests geopolitical dimension)
- **Named persons** — every `PERSON` entity detected by SpaCy was appended to the tags list

**Output: `COMMON-PROCESSED.csv`**
```
┌─────────┬────────────────────────────────────┬────────────────────┬───────────────┬────────────────────┬──────────────────┬──────────────────────────────────────┐
│ Article │ Headline                           │ Headline Sentiment │ Offense Rating│ Negative Words     │ Offensive Words  │ Tags                                 │
├─────────┼────────────────────────────────────┼────────────────────┼───────────────┼────────────────────┼──────────────────┼──────────────────────────────────────┤
│ 1       │ Elon Musk isn't serious about...   │ Somewhat Negative  │ 280           │ foolish, broke...  │ hell             │ Elon, Musk, harassment, Hunter Biden │
│ 2       │ Tesla delivered a record 1.3M...   │ Somewhat Negative  │ 150           │ disappoint,fears.. │ -                │ -                                    │
└─────────┴────────────────────────────────────┴────────────────────┴───────────────┴────────────────────┴──────────────────┴──────────────────────────────────────┘
```

---

### Module 4 — Dashboard (Tableau)

After merging `COMMON.csv` and `COMMON-PROCESSED.csv` into `COMMON-ANALYSIS.csv` using Pandas, the final dataset was fed into Tableau. This was the output layer — the "face" of the product that judges and end-users would see.

The final merged CSV had **all fields in one flat table:**
`Article`, `Title`, `Description`, `URL`, `Content`, `Published`, `Headline`, `Headline Sentiment`, `Offense Rating`, `Negative Words`, `Offensive Words`, `Tags`

We designed **8 dashboard sheets** to tell a data story:

1. **Article Count & Publisher Distribution** — which outlets covered this company, how many articles
2. **Publication Timeline** — when the coverage peaked (date-based line/bar chart)
3. **Headline Sentiment Breakdown** — pie/bar showing the mix of Extremely Negative / Somewhat Negative / Neutral / Positive
4. **Offense Rating Leaderboard** — ranked articles by risk score, highest to lowest
5. **Negative Word Cloud / Frequency** — which negative words appeared most
6. **Offensive Word Occurrences** — similar, for the high-weight offensive vocabulary
7. **Tags Analysis** — breakdown of `lawsuit`, `harassment`, `country` tags, plus named persons
8. **Full Article Detail View** — drill-through table with all fields for any selected article

Because the dashboard read from `COMMON-ANALYSIS.csv`, every time the Python pipeline ran on a new company name and overwrote the CSV, Tableau refreshed automatically. **One input → one refresh → eight updated visualizations.**

![Tableau Dashboard 1](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.1.png)
![Tableau Dashboard 2](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.2.png)
![Tableau Dashboard 3](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.3.png)
![Tableau Dashboard 4](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.4.png)
![Tableau Dashboard 5](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.5.png)
![Tableau Dashboard 6](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.6.png)
![Tableau Dashboard 7](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.7.png)
![Tableau Dashboard 8](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.8.png)

---

## 5. The Data Pipeline in Detail

Here is the full end-to-end flow of the pipeline, from user input to Tableau:

```
┌──────────────────────────────────────────────────────────────────┐
│                    USER RUNS SCRAPER.py                          │
│                    → enters company name                         │
└───────────────────────────────┬──────────────────────────────────┘
                                │
                    scrape_news(organization)
                                │  NewsAPI → up to 10 articles
                    write_to_csv(organization, articles)
                                │  trafilatura full-text extraction
                                │  cleanup_text() regex cleaning
                                ▼
                         ┌──────────────┐
                         │  COMMON.csv  │  Article, Title, Desc,
                         │              │  URL, Content, Published
                         └──────┬───────┘
                                │
                    process_csv(organization)
                                │  BERT sentiment on headline
                                │  SpaCy roBERTa NER on body
                                │  Word-list scoring × 4 lists
                                │  Tag generation
                                ▼
                   ┌───────────────────────┐
                   │ COMMON-PROCESSED.csv  │  Article, Headline,
                   │                       │  Sentiment, Score,
                   │                       │  NegWords, OffWords, Tags
                   └──────────┬────────────┘
                              │
              merge_csv(COMMON.csv, COMMON-PROCESSED.csv)
                              │  pandas merge on Article column
                              ▼
                    ┌──────────────────────┐
                    │  COMMON-ANALYSIS.csv │  All fields merged
                    └──────────┬───────────┘
                               │
                   final_cleanup() × 2 passes
                               │  fill NaN with '-'
                               │  strip list brackets from strings
                               ▼
                    ┌──────────────────────┐
                    │  COMMON-ANALYSIS.csv │  Clean, Tableau-ready
                    │  (final version)     │
                    └──────────┬───────────┘
                               │
                    Tableau reads CSV → 8 dashboards refresh
                               │
                    visualize() → displacy NER in browser
```

---

## 6. Word Stores — The "Weighted List" System

One of the most creative parts of our solution was the custom-built **word store** system. Rather than relying purely on model-based sentiment scoring (which can be slow and opaque), we implemented a transparent, auditable, weighted-vocabulary layer.

The `word-store/` directory contained five text files, each curated by hand:

### `negative_words.txt` (~41KB, thousands of words)
A broad vocabulary of negative, pessimistic, and distressing language: `abominable`, `crisis`, `failure`, `loser`, `absurd`, `condemned`, `panic`, `scandal`, `terrible`, `worst`, etc. Each match added **+10** to the offense rating.

### `bad_words.txt` (~1,275 entries)
A comprehensive list of profanity, slurs, and highly offensive content. Each match added **+50** to the offense rating — a high penalty reflecting how rare and serious such language is in corporate news coverage. The presence of even one of these words in an article about a major company is a significant red flag.

### `lawsuits.txt` (~55 entries)
Legal and judicial vocabulary: `accusation`, `allegation`, `arraignment`, `ban`, `damages`, `embargo`, `embezzlement`, `indictment`, `infringement`, `injunction`, `lawsuit`, `prosecution`, `stealing`, `theft`, `trial`, `unlawful`, `writ`, etc. Each match added **+30**.

### `harassment.txt` (~34 entries)
Workplace misconduct and social-justice flags: `assault`, `bigotry`, `discrimination`, `harassment`, `hatred`, `injustice`, `job-cuts`, `layoffs`, `malpractice`, `maltreatment`, `molestation`, `oppression`, `persecution`, `prejudice`, `rape`, `unfair`, `union`, `unionize`. Each match added **+50**.

### `countries.txt` (195 country names)
All UN-recognised sovereign states. Any country mention was added as a `"country"` tag — useful for spotting when a company is being reported on in a geopolitical context (sanctions, trade disputes, supply chain exposure).

### `companies.txt`
A supplementary list of brand names and companies for cross-reference (Samsung, Nike, Adidas, Honda, etc.).

---

## 7. The Tech Stack

| Layer | Tool / Library | Purpose |
|-------|----------------|---------|
| **Scraping** | `newsapi-python` | News article discovery via NewsAPI |
| **Content Extraction** | `trafilatura` | Boilerplate-free full article text extraction |
| **HTML Parsing** | `BeautifulSoup4` | Headline (`<h1>`) extraction from raw HTML |
| **HTTP** | `requests` | Fetching web pages for headline extraction |
| **Sentiment Analysis** | `transformers` (HuggingFace) + `torch` | BERT multilingual sentiment model (`nlptown/bert-base-multilingual-uncased-sentiment`) for 1–5 star scoring |
| **NLP / NER** | `spacy` (`en_core_web_trf`) | roBERTa-based transformer model for named entity recognition |
| **Sentiment (secondary)** | `spacytextblob` | SpaCy-integrated TextBlob sentiment (auxiliary) |
| **Data Processing** | `pandas` | CSV merging, column cleaning, fillna operations |
| **Text Cleaning** | `re` (regex) | Custom text normalisation pipeline |
| **CLI / UX** | `rich` | Beautiful terminal output — banners, panels, progress tracking, colour-coded status |
| **Visualisation** | `matplotlib` | In-process plotting (auxiliary) |
| **Dashboard** | **Tableau** | 8-sheet interactive dashboard from the final merged CSV |
| **File I/O** | `csv`, `os`, `json` | CSV reading/writing, environment variable access |
| **Warnings** | `warnings` | Suppressed FutureWarnings from transformers |
| **Platform** | `platform` | OS detection for terminal width calculation |

**Python version:** 3.x  
**NLP Model:** `en_core_web_trf` (SpaCy English transformer, roBERTa backbone)  
**Sentiment Model:** `nlptown/bert-base-multilingual-uncased-sentiment` (HuggingFace)

---

## 8. The Code — SCRAPER.py Walkthrough

The entire pipeline lives in a single file: `SCRAPER.py`. Here is a function-by-function breakdown:

### Utility Functions

```
parse_text_from_web(webURL)
```
Downloads a URL with `trafilatura`, extracts only the main article body (no ads, no comments, no tables, no images), and returns clean English text.

```
cleanup_text(text)
```
Regex-based text normaliser. Strips special characters (keeping alphanumeric, spaces, and periods), removes leading/trailing whitespace, drops non-ASCII characters, and re-joins word tokens while fixing space-before-period artifacts.

### Scraping

```
scrape_news(organization)
```
Authenticates against NewsAPI using an environment variable `NEWSAPI`, then calls `get_everything()` with the organisation name as query, a date range, English language filter, and relevancy sort. Returns up to 10 articles.

```
write_to_csv(organization, all_articles)
```
Iterates the API response, calls `parse_text_from_web()` on each article URL, cleans the content, and writes `Article | Title | Description | URL | Content | Published` to `CSVs/COMMON.csv`. Rich-formatted console output for each successful write.

### Sentiment & Processing

```
get_headline(content, organization)
```
Fetches the article URL, parses it with BeautifulSoup, and extracts the first `<h1>` tag as the headline. Falls back to `"No Headline"` if none is found or the text is too short.

```
sentiment_score_to_summary(sentiment_score)
```
Converts integer 1–5 to a human-readable label (Extremely Negative → Extremely Positive).

```
sentiment_analysis(content)
```
Tokenises the input text using the BERT tokenizer (with truncation/padding), runs the classification model, takes `argmax` of logits, and returns the sentiment label.

```
process_csv(organization)
```
The core processing loop. Loads all five word-store files. Reads `COMMON.csv` row by row. For each article:
- Extracts headline and scores its sentiment via `sentiment_analysis()`
- Initialises `offense_rating = 0`
- Adds 200 or 100 to offense rating based on headline sentiment
- Runs `nlp(raw_text)` through SpaCy
- Iterates every word token checking against all four word lists
- Collects negative words, offensive words, and tags
- Applies a small normalisation (-10 if offense_rating > 20)
- Writes to `COMMON-PROCESSED.csv`

### Merging & Cleanup

```
merge_csv(csv1, csv2, organization)
```
Pandas merge of `COMMON.csv` and `COMMON-PROCESSED.csv` on the `Article` column. Saves to `COMMON-ANALYSIS.csv`.

```
final_cleanup(organization)
```
Post-processing pass (run twice for safety):
- Fills NaN cells in `Offensive Words`, `Negative Words`, `Tags` with `'-'`
- Strips Python list brackets (`[`, `]`, `'`) from stringified list fields so Tableau can parse them cleanly

```
visualize(organization)
```
Concatenates all article content from `COMMON.csv`, runs SpaCy NER on the full corpus, and serves a `displacy` entity visualizer on localhost so you can browse the tagged text in your browser.

### Main Execution Block

```python
console = Console(...)
print_banner(console)          # ASCII art "MEDIA ANALYSIS" banner
organization = input()          # User types company name
articles = scrape_news(organization)
write_to_csv(organization, articles)
process_csv(organization)
merge_csv('CSVs/COMMON.csv', 'CSVs/COMMON-processed.csv', organization)
final_cleanup(organization)
final_cleanup(organization)     # Run twice for idempotent cleanup
visualize(organization)         # Open displacy in browser
```

The terminal UI used `rich` throughout for colour-coded output, status panels, and the ASCII art banner (the word "MEDIA ANALYSIS" rendered in large block letters).

---

## 9. Companies Analysed

During development and demonstration, the pipeline was run against **33 distinct companies/topics**, producing three CSVs each (raw, processed, analysis). The breadth of the test set was intentional — we wanted to demonstrate the system worked across industries, geographies, and entity types:

| Category | Companies / Topics |
|----------|--------------------|
| **Tech Giants** | Microsoft, NVIDIA, GitHub, Firebase, Salesforce |
| **Social Media** | Facebook, Reddit, Snapchat, YouTube |
| **EV / Automotive** | Tesla, Vivo, Lenovo |
| **Energy** | ExxonMobil |
| **Entertainment** | Marvel, Crunchyroll, Ubisoft (gaming), Pitchfork (music media) |
| **Food & FMCG** | Zomato, Swiggy, Maggi (Nestlé), Unilever, Tupperware |
| **Consumer Goods** | Titan, Skullcandy, Reliance |
| **Finance** | Barclays |
| **AI / Tech Topics** | ChatGPT (GPT-3), Python (programming language), FreeCodeCamp |
| **Logistics** | Porter |
| **Dating** | Tinder |

The resulting CSVs are all preserved in the `CSVs/` directory and form the demo dataset. The combined COMMON-ANALYSIS file (`CSVs/COMMON-ANALYSIS.csv`) was the one fed into the Tableau workbook (`FINAL_ANALYSIS.twb`).

---

## 10. Obstacles, Setbacks, and War Stories

No hackathon goes smoothly. Here is an honest account of everything that made this hard:

### 🕸️ Web Scraping Hell
Getting clean article text was far harder than expected. Most news sites serve JavaScript-rendered content, have aggressive bot detection, return 403/404 errors, or have layouts so varied that generic parsers fail. `trafilatura` was the hero here — it handled the majority of sites gracefully — but there were still many articles where `content` came back as `None`, which required robust null-checking throughout the pipeline.

### 🔤 UTF-8 Encoding Disasters
Multi-byte characters, smart quotes, em-dashes, and non-Latin scripts all caused CSV corruption and downstream Tableau parsing errors. The solution was `.encode('ascii', 'ignore').decode('ascii')` in `cleanup_text()` — a brute-force strip of anything non-ASCII. It wasn't elegant, but it worked. (There's even a `# TODO: prevent utf-8 encoding errors in CSVs` comment at the top of the file — evidence that this was an ongoing battle.)

### 🕰️ API Throttling
NewsAPI's free tier has strict rate limits. Hitting those limits mid-run during the hackathon caused silent failures that were difficult to diagnose. We wrapped the API call in a bare `except Exception: pass` block to keep the pipeline alive, though this made debugging harder.

### 🧠 NLP Processing Speed
Running `en_core_web_trf` (a full roBERTa transformer) on 10 full-length news articles sequentially is slow. Each article could take 10–30 seconds on CPU. With a hackathon clock ticking, this was nerve-wracking. We could not easily parallelise it without more time, so we accepted the latency and focused on output quality.

### 🎯 Module 3 — Custom Risk NER
Adding our own "risk entity" support on top of SpaCy's pre-trained model was conceptually the hardest part. SpaCy's roBERTa model knows how to tag `PERSON`, `ORG`, `GPE` etc., but it has no concept of "this word means the company is being sued" or "this sentence contains a harassment allegation." We solved this not by fine-tuning the model (too slow for a hackathon), but by implementing the word-list layer *alongside* SpaCy — a hybrid symbolic-neural approach. For each token, we checked it against both SpaCy's entity tagger *and* our custom word stores. This gave us speed (word lookups are O(1) with sets) without sacrificing the nuance of transformer-based NER.

### 📊 Tableau — Zero Experience, 2-Hour Crash Course
None of us had ever used Tableau before. We ran a 2-hour crash course on the fly during the hackathon, working through tutorials while simultaneously building our dashboards. The learning curve was steep. Understanding data types, measures vs. dimensions, calculated fields, and dashboard layout all had to happen in real time. Somehow we emerged with 8 polished sheets.

### 🔗 Date Parsing
Published timestamps from NewsAPI came in ISO 8601 format (`2022-12-21T01:57:28Z`). Tableau has opinions about how dates should be formatted. Ensuring the `Published` column was interpreted correctly as a date dimension (not a string) required some careful CSV formatting and Tableau data-type configuration.

### 🐛 The Double `final_cleanup()` Call
You will notice `final_cleanup(organization)` is called twice in the main execution block. This is not a bug — it is a pragmatic fix. The first pass cleaned list brackets from string representations of Python lists. The second pass caught any cases where the first pass had introduced edge cases. Not pretty, but it worked.

---

## 11. Results & Rewards

We competed against **36 other teams** — roughly **140+ participants** — and made it through all rounds to the final.

The final round was an interview-style project presentation to a panel of CRIF judges. We demonstrated the live pipeline, walked through the architecture, explained every design decision, and showed the Tableau dashboards refreshing in real time.

**We secured first place.**

The rewards:

| Prize | Value |
|-------|-------|
| 💰 Cash Prize | **₹50,000** |
| 🎁 Goodies | For each team member |
| 🏆 Trophy | "Winner Takes It All" team trophy |
| 📜 Certificate | Victory certificate for each team member |

The win was a validation of the architecture — particularly the hybrid NLP + symbolic scoring approach, the breadth of test data (33 companies), and the polish of the Tableau presentation layer.

---

## 12. Retrospective from 2026

*It is May 2026. Three years have passed since we pulled this off. Here's what I think about it now.*

### What We Got Right

**The idea was ahead of its time in the right way.** Back in January 2023, LLMs were just entering mainstream consciousness (ChatGPT had launched in November 2022 — and yes, we even tested our pipeline against "ChatGPT" as a company/topic). We chose a hybrid approach: a pre-trained BERT/roBERTa model for sentiment + SpaCy's transformer NER + a custom symbolic scoring layer. That combination was genuinely the right call for a time-constrained hackathon. Fully fine-tuning a risk-domain model was not feasible in 24–48 hours. A pure rules-based system would have been too brittle. The hybrid was the Goldilocks solution.

**The three-CSV pipeline was elegant.** Raw → Processed → Analysis is a clean, auditable data lineage. Anyone looking at the repo can trace exactly how a piece of text became a risk score. In 2026, "data lineage" and "explainable AI" are table-stakes requirements in regulated industries like banking and insurance. We were doing it — crudely, manually — three years ago.

**The Tableau strategy was smart.** Rather than building a custom web frontend (which would have taken most of the hackathon), we used a professional BI tool that judges recognised and trusted. The auto-refresh-on-CSV-overwrite trick meant we could show the full pipeline running live in the presentation — type a company name, watch the CSVs populate, watch the dashboards update. That was the memorable demo moment.

### What We Would Do Differently in 2026

**Replace the word-store scoring with a proper risk LLM.** In 2026, you would fine-tune a small open-weights LLM (say, a 7B parameter model via LoRA) on a labelled dataset of risk-tagged news sentences. The word-list approach, while transparent and fast, is brittle — it scores articles about a company's "fire" sale the same as articles about an actual fire. A context-aware model would handle this correctly.

**Switch to a streaming architecture.** The batch pipeline (scrape → write → process → merge → clean) was a hackathon design. A production system would use something like Kafka or Pulsar for event-driven article ingestion, with a stream processor doing NER and scoring in near-real-time as articles arrive.

**Add entity disambiguation.** One of the pain points in the NER output was that "Apple" the company and "apple" the fruit, or "Amazon" the company and the river, needed disambiguation. SpaCy's `en_core_web_trf` does this reasonably well in context, but we weren't doing any post-processing to deduplicate or resolve entity mentions.

**Multi-source scraping.** We were limited to NewsAPI's coverage. A production version would aggregate RSS feeds, Reddit mentions (`r/investing`, `r/stocks`), Twitter/X sentiment, regulatory filings (SEC EDGAR, Companies House), and court records. The CRIF problem statement specifically mentioned DuckDuckGo and Yahoo — we used only NewsAPI because it was the most reliable within the hackathon window.

**Proper API key management.** The `NEWSAPI` key was stored in an environment variable — correct. But the code had placeholder TODO comments and hard-coded date windows that would need parameterisation for production use.

### The Bigger Picture

What we built in 2023 was a prototype for what, by 2026, has become a category of enterprise software: **AI-powered media reputation monitoring**. Companies like Meltwater, Brandwatch, Signal AI, and a dozen VC-backed startups now sell exactly this kind of product to banks, law firms, and procurement departments. CRIF themselves have continued investing in alternative data and non-financial risk scoring.

We were three-years-ago students with a problem statement, Python, and a lot of caffeine. The architecture we chose was sound. The execution was solid enough to beat 36 other teams. And the core insight — that you can quantify reputational risk from unstructured news text using NLP — turned out to be commercially correct.

Not bad for a hackathon.

---

## 13. Repository Structure

```
CRIF-Hackathon-2023/
│
├── SCRAPER.py                          # The entire Python pipeline (all 4 modules)
├── README.md                           # Original project README
├── CRIF-Hackathon-2023.md              # This archive note (written in 2026)
├── FINAL_ANALYSIS.twb                  # Tableau workbook (8-sheet dashboard)
├── CRIF-Hackathon-2023-Problem-Statements.docx  # Original problem statement document
│
├── CSVs/                               # All data artifacts
│   ├── COMMON.csv                      # Active: raw scraped articles (overwritten each run)
│   ├── COMMON-PROCESSED.csv            # Active: sentiment + scoring results
│   ├── COMMON-ANALYSIS.csv             # Active: merged final dataset (Tableau input)
│   │
│   ├── FINAL_ANALYSIS.twb              # Tableau workbook copy
│   ├── barclays.csv                    # Demo run: Barclays (raw only)
│   │
│   │   ── [company].csv               # Raw scraped articles (33 companies)
│   │   ── [company]-processed.csv     # Processed/scored articles
│   │   ── [company]-ANALYSIS.csv      # Merged final analysis
│   │
│   │   Companies: Reliance, Swiggy, Tinder, Vivo, chatgpt3, cnbc, crunchyroll,
│   │              exxon mobil, facebook, firebase, freecodecamp, github, lenevo,
│   │              maggi, marvel, microsoft, nvidia, pitchfork, porter, python,
│   │              reddit, salesforce, skullcandy, snapchat, tesla, titan,
│   │              tupperware, ubisoft, unilever, youtube, zomato
│
├── word-store/                         # Custom curated vocabulary lists
│   ├── negative_words.txt              # ~thousands of negative/pessimistic words (+10 each)
│   ├── bad_words.txt                   # ~1,275 offensive/profane words (+50 each)
│   ├── lawsuits.txt                    # ~55 legal/judicial terms (+30 each)
│   ├── harassment.txt                  # ~34 misconduct/discrimination terms (+50 each)
│   ├── countries.txt                   # 195 sovereign nation names (tags only)
│   └── companies.txt                   # Brand/company reference list
│
└── assets/                             # Screenshots for README documentation
    ├── CRIF 1.jpeg                     # Hackathon event photo
    ├── CRIF 2.jpg                      # Hackathon event photo
    ├── module1.png                     # Screenshot: Scraper output
    ├── module2.png                     # Screenshot: NER tagging
    ├── module3.png                     # Screenshot: Scoring/processing
    ├── module4.1.png                   # Tableau dashboard sheet 1
    ├── module4.2.png                   # Tableau dashboard sheet 2
    ├── module4.3.png                   # Tableau dashboard sheet 3
    ├── module4.4.png                   # Tableau dashboard sheet 4
    ├── module4.5.png                   # Tableau dashboard sheet 5
    ├── module4.6.png                   # Tableau dashboard sheet 6
    ├── module4.7.png                   # Tableau dashboard sheet 7
    └── module4.8.png                   # Tableau dashboard sheet 8
```

---

## 14. Original README (preserved verbatim)

*The following is the original README.md from the repository, preserved exactly as written at the time of the hackathon.*

---

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

2. Gurjas Gandhi - Administration, Mangement, Insightful Feedback,Generating Tableau Dashboards.

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

![MODULE 1](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module1.png)
![MODULE 2](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module2.png)
![MODULE 3](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module3.png)

**Tableau** - Taking input of the `COMMON-ANALYSIS.csv` file, we designed 8 dashboards to present or narrate a story with all our data. Since we had plenty of fields like `Article Count`, `Title`,` Description`, `Content` (which holds the entire article text), `URL`, `Publisher`, `Published Date`, `Headline`, `Headline Sentiment`, `Offensive Rating`, `Negative Words`, `Offensive Words and Tags` it was not much of a hassle. We made good use of several plotting and graphing methods and presented a diverse yet insightful story. Each Tableau report updates after looking up a new organization.

![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.1.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.2.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.3.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.4.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.5.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.6.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.7.png)
![VISUALIZATION](https://github.com/HighnessAtharva/CRIF-Hackathon-2023/blob/main/assets/module4.8.png)

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

---

*End of original README.*

---

*— Atharva Shah, archived May 2026*
