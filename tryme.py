from newspaper import Article

url="https://beebom.com/lenovo-tab-p11-5g-launched-india/"

article=Article(url)
article.download()
article.parse()
article.nlp()