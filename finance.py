ticks={
    "Google": "GOOG",
    "Amazon": "AMZN",
    "Flipkart": "FPKT",
    "Apple": "AAPL",
    "Netflix": "NFLX",
    "Tesla": "TSLA",
    "Facebook": "META",
}


import yfinance as yf

stock=yf.Ticker("GOOG")
history = stock.history(period='1wk')
print(history)
print(stock.info)
