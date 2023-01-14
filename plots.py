import matplotlib as plt
import pandas as pd
import csv

data = pd.read_csv('CSVs/cnbc-ANALYSIS.csv', encoding='utf-8', index_col=0)
data.head()