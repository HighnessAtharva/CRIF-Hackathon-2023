# Description: Get ticker symbol from company name
import requests
import json


def getticker(companyname):
    # sourcery skip: inline-immediately-returned-variable, remove-unnecessary-else, swap-if-else-branches
    # set base url
    url = "http://d.yimg.com/autoc.finance.yahoo.com/autoc"

    # set parameters
    params = {
        "query": {companyname},
        "region":1,
        "lang":"en"
    }

    # make request
    response = requests.get(url, params=params)
    # check status code
    if response.status_code == 200:
        # get json response
        data = response.json()
        # get company data
        company_data = data['ResultSet']['Result'][0]
        # get ticker
        ticker = company_data['symbol']
        # return ticker
        return ticker
    else:
        # return None
        return None

