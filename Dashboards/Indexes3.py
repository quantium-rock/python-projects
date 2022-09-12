
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from math import isnan
from datetime import datetime as dt
import matplotlib.pyplot as plt
from sqlalchemy import create_engine

pd.set_option('mode.chained_assignment', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

configOanda = open('C:\X-Projects\Python\Dashboards\Oanda.config','r')
GSheet, Token, accountID, *rest = configOanda.read().splitlines()
configOanda.close()
api = oandapyV20.API(access_token=Token)

syms = ['AU200_AUD','CN50_USD','EU50_EUR','FR40_EUR','DE30_EUR','HK33_HKD','IN50_USD','JP225_USD','NL25_EUR','SG30_SGD','TWIX_USD','UK100_GBP','NAS100_USD','US2000_USD','SPX500_USD','US30_USD','DE10YB_EUR','UK10YB_GBP','USB10Y_USD','USB02Y_USD','USB05Y_USD','USB30Y_USD','BCO_USD','WTICO_USD','NATGAS_USD','CORN_USD','SOYBN_USD','SUGAR_USD','WHEAT_USD','XCU_USD','XPT_USD','XPD_USD','XAU_USD','XAG_USD','XAU_AUD','XAU_CAD','XAU_CHF','XAU_EUR','XAU_GBP','XAU_HKD','XAU_JPY','XAU_NZD','XAU_SGD','XAU_XAG','XAG_AUD','XAG_CAD','XAG_CHF','XAG_EUR','XAG_GBP','XAG_HKD','XAG_JPY','XAG_NZD','XAG_SGD','AUD_USD','EUR_USD','GBP_USD','NZD_USD','USD_CAD','USD_CHF','USD_HKD','USD_JPY','USD_SGD','AUD_CAD','AUD_CHF','AUD_HKD','AUD_JPY','AUD_NZD','AUD_SGD','CAD_CHF','CAD_HKD','CAD_JPY','CAD_SGD','CHF_HKD','CHF_JPY','EUR_AUD','EUR_CAD','EUR_CHF','EUR_GBP','EUR_HKD','EUR_JPY','EUR_NZD','EUR_SGD','GBP_AUD','GBP_CAD','GBP_CHF','GBP_HKD','GBP_JPY','GBP_NZD','GBP_SGD','HKD_JPY','NZD_CAD','NZD_CHF','NZD_HKD','NZD_JPY','NZD_SGD','SGD_CHF','SGD_HKD','SGD_JPY','EUR_DKK','EUR_NOK','EUR_SEK','USD_DKK','USD_NOK','USD_SEK','CHF_ZAR','EUR_CZK','EUR_HUF','EUR_PLN','EUR_TRY','EUR_ZAR','GBP_PLN','GBP_ZAR','TRY_JPY','USD_CNH','USD_CZK','USD_HUF','USD_INR','USD_MXN','USD_PLN','USD_SAR','USD_THB','USD_TRY','USD_ZAR','ZAR_JPY']
tf = 'D'; ln = 10

def getAssets(syms):
    assets = []; ccys = {}
    for sym in syms:
        split = sym.split('_')
        if split[0] not in assets:
            assets.append(split[0])
        if split[1] not in assets:
            assets.append(split[1])
        assets = sorted(assets)
        try:
            ccys[split[0]].append(split[1])
        except:
            ccys[split[0]] = []
            ccys[split[0]].append(split[1])
        try:
            ccys[split[1]].append(split[0])
        except:
            ccys[split[1]] = []
            ccys[split[1]].append(split[0])
    return assets, ccys

assets, ccys = getAssets( syms )

def getPrs( sym, tf, ln ):
    params = { 'granularity': tf, 'count': ln }
    oan = instruments.InstrumentsCandles( instrument=sym, params=params )
    prs = pd.DataFrame(api.request(oan)['candles'])
    Ln = len(prs); t, p = [], []
    for i in range(Ln):
        if prs['complete'][i]:
            t.append(dt.strptime(prs['time'][i][:10],'%Y-%m-%d'))
            p.append(float(prs['mid'][i]['c']))
    prs = pd.DataFrame({'Date':t,'Price':p,})
    return prs

def getHist( syms, tf, ln ):
    hist = {}; dates = []
    for sym in syms:
        prs = getPrs( sym, tf, str(ln) )
        base, term = sym.split('_')
        for i in range(ln-1):
            wkd = dt.weekday(prs['Date'][i])
            if wkd < 5:
                date = str(prs['Date'][i])[:10]
                dates.append(date)
                hist.update( {(date, base, term): prs['Price'][i]} )
    dates = pd.np.unique(dates)
    return hist, dates

hist, dates = getHist( syms, tf, ln )

def initMtx( dates, assets ):
    mtx = {}
    for date in dates:
        mtx[date] = pd.DataFrame( data= 0.0, index=assets, columns=assets )
    return mtx

mtx = initMtx( dates, assets )

def addMtx():
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

addMtx()

def checkMtx( date ):
    for x in assets:
        for y in assets:
            if mtx[date][x][y] == 0: 
                return False
    return True

def cmpltMtx():
    cmplt = False
    for date in dates:
        while not cmplt:
            for x in assets:
                for y in assets:
                    if mtx[date][x][y] == 0:
                        if mtx[date][ccys[x]][ccys[y]] != 0:
                            mtx[date][x][y] = mtx[date][x][ccys[x]]/mtx[date][y][ccys[y]]*mtx[date][ccys[x]][ccys[y]]
            complt = checkMtx(date)

cmpltMtx()

mtx[dates[1]]
ccys['XAU']
syms



def getIdx():
    idx = pd.DataFrame(index=dates,columns=assets)
    for date in dates:
        for ass in assets:
            idx[ass][date] = mtx[date][ass].mean(skipna=False)
    idx = idx.replace([pd.np.inf, -pd.np.inf], pd.np.nan)
    idx = idx.dropna()
    idx = idx.sort_index(ascending=False)
    return idx

idx = getIdx()

def Comp(i,X,Y):
    index = idx.index
    Base = idx[X][index[i]].mean()
    Term = idx[Y][index[i]].mean()
    Synt = Base/Term
    Real = mtx[index[i]][X][Y]
    dec = len(str(Real).split('.')[1])
    Synt = round(Synt,dec)
    print(dates[i],"Synt= ",Synt,"Real= ",Real)

Comp(3,'SPX500','EUR')

Accuracy()            


def Accuracy():
    accuracy = {}
    for x in assets:
        for y in assets:
            sym = x+'_'+y
            accuracy[sym] = pd.DataFrame(index=dates,columns=['Accuracy'])
            for date in dates:
                accu = 1.0
                try:
                    base = idx[x][date]
                    term = idx[y][date]
                    synt = base/term
                    real = mtx[date][x][y]
                    accu = synt/real
                except:
                    pass
                accuracy[sym][date] = accu
    return accuracy
            
                
accuracy = Accuracy()
accuracy

idx['SPX500']['2020-01-22']

mtx['2020-01-22']

            

    
