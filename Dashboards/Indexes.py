
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
params = {'granularity': 'D', 'count': '10'}

def getHistory( symbol, timeframe, periods ):
    params = {'granularity': timeframe, 'count': periods}
    r = instruments.InstrumentsCandles(instrument=symbol,params=params)
    df = pd.DataFrame(api.request(r)['candles'])
    df
    Len = len(df); t, p, v = [], [], []
    for i in range(Len):
        if df['complete'][i]:
            t.append(dt.strptime(df['time'][i][:10],'%Y-%m-%d'))
            p.append(float(df['mid'][i]['c']))
            v.append(int(df['volume'][i]))
    df = pd.DataFrame({'Date':t,'Price':p,'Volume':v})
    df = df.set_index('Date')
    return df

tf = 'D'; ln = 10

syms = ['EUR_USD','USD_JPY','GBP_USD','BCO_USD','SPX500_USD']

hist = {}
for sym in syms:
    hist[sym] = getHistory(sym,tf,str(ln))

assets = []
for sym in syms:
    split = sym.split('_')
    if split[0] not in assets:
        assets.append(split[0])
    if split[1] not in assets:
        assets.append(split[1])

assets = sorted(assets)

idx = {}
for ass in assets:
    idx[ass] = []
for i in range(ln-1):
    matrix = pd.DataFrame(data= 0.0, index=assets, columns=assets)
    for sym in syms:
        split = sym.split('_')
        price = hist[sym]['Price'][i]
        matrix[split[0]][split[1]] = price
        matrix[split[1]][split[0]] = 1/price
    zero = True
    while zero:
        for x in assets:
            for y in assets:
                if matrix[x][y] == 0:
                    if x == y:
                        matrix[x][y] = 1.0
                    xy, xcc, yx, ycc = 0, 0, 0, 0
                    for xx in assets:
                        if len(xx) == 3:
                            if matrix[x][xx] != 0 and matrix[x][xx] != 1:
                                xcc = xx
                                xy = matrix[x][xx]
                                break
                    for yy in assets:
                        if len(yy) == 3:
                            if matrix[y][yy] != 0 and matrix[y][yy] != 1:
                                ycc = yy
                                yx = matrix[y][yy]
                                break
                    if xcc == ycc:
                        matrix[x][y] = xy / yx
                        matrix[y][x] = yx / xy
                    else:
                        if matrix[xcc][ycc] != 0:
                            matrix[x][y] = xy / yx * matrix[xcc][ycc]
                            matrix[y][x] = 1/matrix[x][y]
        for x in assets:
            for y in assets:
                if matrix[x][y] == 0:
                    zero = True
                else: zero = False
    for ass in assets:
        mean = matrix[ass].mean()
        idx[ass].append(mean)

print(matrix)
print(idx)

plt.figure(0)
for ins in idx.keys():
    plt.plot(idx[ins])
    plt.legend(ins)

plt.show()




syms = ['EUR_USD','USD_JPY','GBP_USD','BCO_USD','SPX500_USD','EUR_GBP','GBP_JPY','GBP_NZD']
tf = 'D'; ln = 10

def getAssets(symbols):
    assets = []; ccys = []
    for sym in syms:
        split = sym.split('_')
        if split[0] not in assets:
            assets.append(split[0])
        if split[1] not in assets:
            assets.append(split[1])
        if split[1] not in ccys:
            ccys.append(split[1])
    assets = sorted(assets)
    ccys = sorted(ccys)
    return assets, ccys

assets, ccys = getAssets(syms)

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
    for date in dates:
        for x in ccys:
            for y in ccys:
                if fx[date][x][y] == 0:
                    k = []; w = []
                    for z in ccys:
                        if z != x and z != y:
                            xz = fx[date][x][z]
                            yz = fx[date][y][z]
                            if xz != 0 and yz != 0:
                                k.append(fx[date][x][z])
                                w.append(fx[date][y][z])
                    kl = len(k)
                    wl = len(w)
                    if kl < 1 or wl < 1:
                        print('No ccys to compare!')
                    else:
                        fx[date][x][y] = (sum(k)/kl) * (sum(w)/wl)

def endFX():
    z = True
    while z:
        for date in dates:
            for x in ccys:
                for y in ccys:
                    if fx[date][x][y] == 0:
                        for xx in ccys:
                            for yy in ccys:
                                if x != xx and fx[date][x][xx] != 0:
                                    if y != yy and fx[date][y][yy] != 0:
                                        print(x,xx,y,yy)
                                        break
                                        fx[date][x][y] = fx[date][y][yy]/fx[date][x][xx]
                                        fx[date][y][x] = fx[date][x][xx]/fx[date][y][yy]
            for x in ccys:
                for y in ccys:
                    if fx[date][x][y] == 0:

                        z = True
                        break
                    else: z = False

endFX()

fx[dates[0]]








for sym in symbols:
    split = sym.split('_')
    price = hist[sym]['Price'][i]
    matrix[split[0]][split[1]] = price
    matrix[split[1]][split[0]] = 1/price
zero = True
while zero:
for x in assets:
    for y in assets:
        if matrix[x][y] == 0:
            if x == y:
                matrix[x][y] = 1.0

hist

ass

ccys

matrix = 


xccy = pd.DataFrame(data= 0.0, index=ccys, columns=ccys)

xccy




