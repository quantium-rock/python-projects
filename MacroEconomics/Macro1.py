3
import pandas as pd
import time
import datetime as dt
import sys
import os
import matplotlib as plt

df = pd.read_csv("C:\X-Projects\Python\MacroEconomics\economic_calendar.csv")

df['Country']

plt.plot(df)
df
gr = df.filter(like='Germany')
gr
