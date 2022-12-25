import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
import copy
from sklearn.linear_model import LinearRegression

import binance_functions as bf
"""
В PrepareDF функції планується добавити стовпці мін та макс каналу з середніх значеннь з історії,
позиція в каналі та кут нахилу тренду
"""


def PrepareDF(DF):                                                     # Функція формування повного датафрейму
    ohlc = DF
    ohlc.columns = ["date", "open", "high", "low", "close", "volume", "date_2"]  # Зміна назв колонок датафрейму
    ohlc = ohlc.set_index('date')
    df = indATR(ohlc, 14).reset_index()
    df['slope'] = indSlope(df['close'], 5)
    df['chanel_max'] = df['high'].rolling(10).max()
    df['chanel_min'] = df['low'].rolling(10).min()
    df['position_in_channel'] = (df['close'] - df['chanel_min']) / (df['chanel_max'] - df['chanel_min'])
    df = df.set_index('date')
    df = df.reset_index()
    return df


# True Range and Average True Range indicator
def indATR(source_DF, n):
    """
    TR = max[(H-L), |H-Cp|, |L-Cp|]
    ATR = 1/n * sum(TR)
    TR: a particular True Range
    n: the time period employed
    H: current High
    L: current Low
    Cp: previous close
    """
    df = source_DF.copy()
    df['H-L'] = abs(df['high']-df['low'])
    df['H-PC'] = abs(df['high']-df['close'].shift(1))
    df['L-PC'] = abs(df['low']-df['close'].shift(1))
    df['TR'] = df[['H-L', 'H-PC', 'L-PC']].max(axis=1, skipna=False)
    df['ATR'] = df['TR'].rolling(n).mean()
    df_temp = df.drop(['H-L', 'H-PC', 'L-PC'], axis=1)
    return df_temp


def indSlope(series, n):
    array_sl = [j * 0 for j in range(n-1)]
    for j in range(n, len(series)+1):
        y = series[j-n:j]
        x = np.array(range(n))
        x_sc = (x - x.min()) / (x.max() - x.min())
        y_sc = (y - y.min()) / (y.max() - y.min())

        # !!! Спробувати та порівняти інші варіанти
        x_sc = sm.add_constant(x_sc)
        model = sm.OLS(y_sc, x_sc)
        results = model.fit()
        array_sl.append(results.params[-1])
    slope_angle = (np.rad2deg(np.arctan(np.array(array_sl))))
    return np.array(slope_angle)


def isLCC(DF, i):
    df = DF.copy()
    LCC = 0
    if df['close'][i] <= df['close'][i+1] and df['close'][i] <= df['close'][i-1] and df['close'][i+1] > df['close'][i-1]:
        # Local min
        LCC = i - 1
    return LCC

def isHCC(DF, i):
    df = DF.copy()
    HCC = 0
    if df['close'][i] >= df['close'][i + 1] and df['close'][i] >= df['close'][i - 1] and df['close'][i + 1] < df['close'][i - 1]:
        #Local max
        HCC = i
    return HCC

def getMaxMinChannel(DF, n):
    maxx = 0
    minn = DF['low'].max()
    for i in range(1, n):
        if maxx < DF['high'][len(DF) - i]:
            maxx = DF['high'][len(DF) - i]
        if minn > DF['low'][len(DF) - i]:
            minn = DF['low'][len(DF) - i]
    return maxx, minn


def check_if_signal(symbol):
    ohlc = bf.get_futures_klines(symbol, 100) # get last 100 kandels
    prepared_df = PrepareDF(ohlc)
    signal = "" #return value

    i = 98 # 99 is current kandel which is not clossed, 98 is last closed candel, we need 97 to check it is bottom or top


    if isLCC(prepared_df, i - 1) > 0:
        # found bottom -  OPEN LONG
        if prepared_df['position_in_channel'][i-1] < 0.15:
            #close to top of channel
            if prepared_df['slope'][i-1] > prepared_df['slope'][i-2] > prepared_df['slope'][i-3]:
                #found a good enter point for Long
                signal = 'long'

    if isHCC(prepared_df, i - 1) > 0:
        #found top - OPEN SHORT
        if prepared_df['position_in_channel'][i-1] > 0.85:
            #close to top of channel
            if prepared_df['slope'][i-1] < prepared_df['slope'][i-2] < prepared_df['slope'][i-3]:
                # found a good enter point for Short
                signal = 'short'

    return signal


