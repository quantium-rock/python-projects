
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from math import isnan
from sqlalchemy import create_engine
from datetime import datetime as dt
import time
import json
import matplotlib.pyplot as plt

pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

configOanda = open('C:\X-Projects\Python\Dashboards\Oanda.config','r')
GSheet, Token, accountID, *rest = configOanda.read().splitlines()
configOanda.close()
api = oandapyV20.API(access_token=Token)

syms = ['AU200_AUD','CN50_USD','EU50_EUR','FR40_EUR','DE30_EUR','HK33_HKD','IN50_USD','JP225_USD','NL25_EUR','SG30_SGD','TWIX_USD','UK100_GBP','NAS100_USD','US2000_USD','SPX500_USD','US30_USD','DE10YB_EUR','UK10YB_GBP','USB10Y_USD','USB02Y_USD','USB05Y_USD','USB30Y_USD','BCO_USD','WTICO_USD','NATGAS_USD','CORN_USD','SOYBN_USD','SUGAR_USD','WHEAT_USD','XCU_USD','XPT_USD','XPD_USD','XAU_USD','XAG_USD','XAU_AUD','XAU_CAD','XAU_CHF','XAU_EUR','XAU_GBP','XAU_HKD','XAU_JPY','XAU_NZD','XAU_SGD','XAU_XAG','XAG_AUD','XAG_CAD','XAG_CHF','XAG_EUR','XAG_GBP','XAG_HKD','XAG_JPY','XAG_NZD','XAG_SGD','AUD_USD','EUR_USD','GBP_USD','NZD_USD','USD_CAD','USD_CHF','USD_HKD','USD_JPY','USD_SGD','AUD_CAD','AUD_CHF','AUD_HKD','AUD_JPY','AUD_NZD','AUD_SGD','CAD_CHF','CAD_HKD','CAD_JPY','CAD_SGD','CHF_HKD','CHF_JPY','EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_HKD','EUR_JPY','EUR_NZD','EUR_SGD','GBP_AUD','GBP_CAD','GBP_CHF','GBP_HKD','GBP_JPY','GBP_NZD','GBP_SGD','HKD_JPY','NZD_CAD','NZD_CHF','NZD_HKD','NZD_JPY','NZD_SGD','SGD_CHF','SGD_HKD','SGD_JPY','EUR_DKK','EUR_NOK','EUR_SEK','USD_DKK','USD_NOK','USD_SEK','CHF_ZAR','EUR_CZK','EUR_HUF','EUR_PLN','EUR_TRY','EUR_ZAR','GBP_PLN','GBP_ZAR','TRY_JPY','USD_CNH','USD_CZK','USD_HUF','USD_INR','USD_MXN','USD_PLN','USD_SAR','USD_THB','USD_TRY','USD_ZAR','ZAR_JPY']

syms = ['EUR_USD','USD_JPY','GBP_USD','BCO_USD','SPX500_USD','EUR_GBP','GBP_JPY','GBP_NZD']
tf = 'D'; ln = 10

def getAssets(symbols):
    assets = []; ccys = []; symccy = {}
    for sym in syms:
        split = sym.split('_')
        if split[0] not in assets:
            assets.append(split[0])
            symccy[split[0]] = split[1]
        if split[1] not in assets:
            assets.append(split[1])
            symccy[split[1]] = split[0]
        if split[1] not in ccys:
            ccys.append(split[1])
    assets = sorted(assets)
    ccys = sorted(ccys)
    return assets, ccys, symccy

assets, ccys, symccy = getAssets(syms)

def getPrices( symbol, timeframe, periods ):
    params = {'granularity': timeframe, 'count': periods}
    r = instruments.InstrumentsCandles(instrument=symbol,params=params)
    df = pd.DataFrame(api.request(r)['candles'])
    df
    Len = len(df); t, p = [], []
    for i in range(Len):
        if df['complete'][i]:
            t.append(dt.strptime(df['time'][i][:10],'%Y-%m-%d'))
            p.append(float(df['mid'][i]['c']))
    df = pd.DataFrame({'Date':t,'Price':p,})
    return df

def getHistory( symbols, timeframe, periods ):
    hist = {}; dates = []
    for symbol in symbols:
        p = getPrices(symbol,timeframe,str(periods))
        dates.append(list(p['Date']))
        base, term = symbol.split('_')
        for i in range(periods-1):
            date = str(p['Date'][i])[:10]
            hist.update( {(date, base, term): p['Price'][i]} )
    dates = pd.np.unique(dates)
    for i in range(len(dates)):
        dates[i] = str(dates[i])[:10]
    return hist, dates

hist, dates = getHistory(syms,tf,ln)

def setMatrices( dates, assets, ccys ):
    ass = {}; fx = {}
    for key in dates:
        ass[key] = pd.DataFrame(data= 0.0, index=assets, columns=assets)
        fx[key] = pd.DataFrame(data= 0.0, index=ccys, columns=ccys)
    return ass, fx

mtx, fx = setMatrices(dates, assets, ccys)

def initMatrices():
    for date in dates:
        for x in assets:
            for y in assets:
                if x == y:
                    mtx[date][x][y] = 1.0
                else:
                    try:
                        p = hist[date,x,y]
                        mtx[date][x][y] = p
                        mtx[date][y][x] = 1/p
                    except:
                        try:
                            p = hist[date,y,x]
                            mtx[date][x][y] = 1/p
                            mtx[date][y][x] = p
                        except:
                            pass
        for x in ccys:
            for y in ccys:
                if x == y:
                    fx[date][x][y] = 1.0
                else:
                    try:
                        p = hist[date,x,y]
                        fx[date][x][y] = p
                        fx[date][y][x] = 1/p
                    except:
                        try:
                            p = hist[date,y,x]
                            fx[date][x][y] = 1/p
                            fx[date][y][x] = p
                        except:
                            pass

initMatrices()

def endFX():
    z = True
    while z:
        for date in dates:
            for x in ccys:
                for y in ccys:
                    if fx[date][x][y] == 0:
                        for xx in ccys:
                            if fx[date][x][y] == 0:
                                for yy in ccys:
                                    if fx[date][x][y] == 0:
                                        if x != xx and fx[date][x][xx] != 0:
                                            if y != yy and fx[date][y][yy] != 0:
                                                fx[date][x][y] = fx[date][x][xx]/fx[date][y][yy]
                                                fx[date][y][x] = fx[date][y][yy]/fx[date][x][xx]
                                    else: break
                            else: break
            for x in ccys:
                for y in ccys:
                    if fx[date][x][y] == 0:
                        z = True
                        break
                    else: z = False

endFX()

fx[dates[0]]

mtx[dates[0]]

def endMtx():
    z = True
    while z:
        for date in dates:
            for x in assets:
                for y in assets:
                    if mtx[date][x][y] == 0:
                        mtx[date][x][y] = mtx[date][x][symccy[x]]/mtx[date][y][symccy[y]]*mtx[date][symccy[x]][symccy[y]]
            for x in assets:
                for y in assets:
                    if mtx[date][x][y] == 0:
                        z = True
                        break
                    else: z = False

endMtx()



