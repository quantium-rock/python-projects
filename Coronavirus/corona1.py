
from matplotlib import pyplot as plt
import OpenBlender
import pandas as pd
import json

token = '5e7eb30d9516293ee1e24814TiizYTGXkqAIZsZYOGzOFlwwaJs7sy'
startdate = "2020-01-01T06:00:00.000Z"
enddate = "2020-03-31T06:00:00.000Z"

action = 'API_getObservationsFromDataset'
parameters = 

{ 
 'token':token,
 'id_dataset':'5e7a0d5d9516296cb86c6263',
 'date_filter':{
               "start_date":startdate,
               "end_date":enddate},
 'consumption_confirmation':'on' 
}

df = pd.read_json(json.dumps(OpenBlender.call(action, parameters)['sample']), convert_dates=False, convert_axes=False).sort_values('timestamp', ascending=False)

df.reset_index(drop=True, inplace=True)
df.head(10)
df['country_region'][i]

def cases( country ):
    co = pd.DataFrame()
    for i in range(len(df)):
        if df['country_region'][i] == country:
            co = co.append( {'timestamp' : df['timestamp'][i], 'confirmed' : df['confirmed'][i], 'deaths' : df['deaths'][i]} , ignore_index=True)
    return co

SPA = cases('Spain')
USA = cases('United States')

fig = px.histogram(USA, x="total_bill", y="tip", color="sex", marginal="rug", hover_data=df.columns)

df_deaths = df.set_index('country_region')
df_deaths = df_deaths.groupby(df_deaths.index)['deaths'].sum().reset_index()
df_deaths = df_deaths.set_index('deaths')
df_deaths = df_deaths.sort_index()

plt.figure()
plt.plot(df['confirmed'])
plt.ylabel('Confirmed COVID-19 cases')
plt.show()

df_compress = df.dropna(0).select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).apply(lambda x: (x - x.min()) / (x.max() - x.min()))
df_compress['timestamp'] = df['timestamp']
# Now we select the columns that interest us
cols_of_interest = ['timestamp', 'PLATINUM_PRICE_price', 'CRUDE_OIL_PRICE_price', 'COCACOLA_PRICE_price', 'open', 'CORN_PRICE_price', 'TIN_PRICE_price', 'PLATINUM_PRICE_price']
df_compress = df_compress[cols_of_interest]
df_compress.rename(columns={'open':'DOW_JONES_price'}, inplace=True)
# An now let's plot them
from matplotlib import pyplot as plt
fig, ax = plt.subplots(figsize=(17,7))
plt = df_compress.plot(x='timestamp', y =['PLATINUM_PRICE_price', 'CRUDE_OIL_PRICE_price', 'COCACOLA_PRICE_price', 'DOW_JONES_price', 'CORN_PRICE_price', 'TIN_PRICE_price', 'PLATINUM_PRICE_price'], ax=ax)

action = 'API_getOpenTextData'
parameters = {
    'token': token,
    'consumption_confirmation':'on',
    'date_filter':{"start_date":startdate, 
                   "end_date":enddate},
    'sources':[
                # Wall Street Journal
               {'id_dataset' : '5e2ef74e9516294390e810a9', 
                 'features' : ['text']},
                # ABC News Headlines
               {'id_dataset':"5d8848e59516294231c59581", 
                'features' : ["headline", "title"]},
                # USA Today Twitter
               {'id_dataset' : "5e32fd289516291e346c1726", 
                'features' : ["text"]},
                # CNN News
               {'id_dataset' : "5d571b9e9516293a12ad4f5c", 
                'features' : ["headline", "title"]}
    ],
    'aggregate_in_time_interval' : {
              'time_interval_size' : 60 * 60 * 24
    },
    'text_filter_search':['covid', 'coronavirus', 'ncov'] 
}

df_news = pd.read_json(json.dumps(OpenBlender.call(action, parameters)['sample']), convert_dates=False, convert_axes=False).sort_values('timestamp', ascending=False)
df_news.reset_index(drop=True, inplace=True)

df_news.head(20)

interest_countries = ['United States','Canada','China', 'Iran', 'Korea', 'Italy', 'France', 'Germany', 'Spain']

for country in interest_countries:
    df_news['count_news_' + country] = [len([text for text in daily_lst if country.lower() in text]) for daily_lst in df_news['source_lst']]

df_news.reindex(index=df_news.index[::-1]).plot(x = 'timestamp', y = [col for col in df_news.columns if 'count' in col], figsize=(17,7), kind='area')

from os import path
from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator

plt.figure()
plt.imshow(WordCloud(max_font_size=50, max_words=80, background_color="white").generate(' '.join([val for val in df_news['source']])), interpolation="bilinear")
plt.axis("off")
plt.show()
plt.figure()
plt.imshow(WordCloud(max_font_size=50, max_words=80, background_color="white").generate(' '.join([val for val in df_news['source']])), interpolation="bilinear")
plt.axis("off")
plt.show()

action = 'API_getObservationsFromDataset'

parameters = {
 'token':token,
 'id_dataset':'5d4c14cd9516290b01c7d673',
 'aggregate_in_time_interval':{"output":"avg","empty_intervals":"impute","time_interval_size":1440},
 'blends':[
        #Yen vs USD              
    {"id_blend":"5d2495169516290b5fd2cee3","restriction":"None","blend_type":"ts","drop_features":[]},
        # Euro Vs USD
    {"id_blend":"5d4b3af1951629707cc1116b","restriction":"None","blend_type":"ts","drop_features":[]},
        # Pound Vs USD              
    {"id_blend":"5d4b3be1951629707cc11341","restriction":"None","blend_type":"ts","drop_features":[]},
        # Corn Price    
    {"id_blend":"5d4c23b39516290b01c7feea","restriction":"None","blend_type":"ts","drop_features":[]},
        # CocaCola Price     
    {"id_blend":"5d4c72399516290b02fe7359","restriction":"None","blend_type":"ts","drop_features":[]},
        # Platinum price             
    {"id_blend":"5d4ca1049516290b02fee837","restriction":"None","blend_type":"ts","drop_features":[]},
        # Tin Price
    {"id_blend":"5d4caa429516290b01c9dff0","restriction":"None","blend_type":"ts","drop_features":[]},
        # Crude Oil Price
    {"id_blend":"5d4c80bf9516290b01c8f6f9","restriction":"None","blend_type":"ts","drop_features":[]}],
 'date_filter':{"start_date":startdate,"end_date":enddate},
 'consumption_confirmation':'on' 
}

df = pd.read_json(json.dumps(OpenBlender.call(action, parameters)['sample']), convert_dates=False, convert_axes=False)

df.sort_values('timestamp', ascending=False)

df.reset_index(drop=True, inplace=True)

print(df.shape)
df.head()

# Lets compress all into the (0, 1) domain
df_compress = df.dropna(0).select_dtypes(include=['int16', 'int32', 'int64', 'float16', 'float32', 'float64']).apply(lambda x: (x - x.min()) / (x.max() - x.min()))
df_compress['timestamp'] = df['timestamp']
# Now we select the columns that interest us
cols_of_interest = ['timestamp', 'PLATINUM_PRICE_price', 'CRUDE_OIL_PRICE_price', 'COCACOLA_PRICE_price', 'open', 'CORN_PRICE_price', 'TIN_PRICE_price', 'PLATINUM_PRICE_price']
df_compress = df_compress[cols_of_interest]
df_compress.rename(columns={'open':'DOW_JONES_price'}, inplace=True)
# An now let's plot them
from matplotlib import pyplot as plt
fig, ax = plt.subplots(figsize=(17,7))
plt = df_compress.plot(x='timestamp', y =['PLATINUM_PRICE_price', 'CRUDE_OIL_PRICE_price', 'COCACOLA_PRICE_price', 'DOW_JONES_price', 'CORN_PRICE_price', 'TIN_PRICE_price', 'PLATINUM_PRICE_price'], ax=ax)