import copy
import time

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
from futures_sign import send_signed_request, send_public_request
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from cred import KEY, SECRET
import requests

from binance_functions import *
from Indicators import *




def main():


    global client
    symbol = 'ETHUSDT'
    client = Client(KEY, SECRET)

    maxposition = 0.006
    stop_percent = 0.01 # 0.01 = 1%
    eth_proffit_array = [[20, 1], [40, 1], [60, 2], [80, 2], [100, 2], [150, 1], [200, 1], [200, 0]]
    proffit_array = copy.copy(eth_proffit_array)

    pointer = str(rando.randint(1000, 9999))


    starttime = time.time()
    timeout = time.time() + 60 * 60 * 12
    courent = 1

    while time.time() <= timeout:
        try:
            prt("script continue running at "+time.strftime('%Y - %m - %d %H:%M:%S', time.localtime(time.time())))
            main(counterr)
            counterr += 1
            if counterr > 5:
                counterr = 1
            time.sleep(60 - ((time.time() - starttime) % 60.0)) # 1 minute interval between each new execution
        except KeyboardInterrupt:
            print('\n\KeyboardInterrupt. Stopping.')
            exit()





"""

    pd.set_option('display.max_columns', None)  #форматування відображення DataFrame
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_colwidth', None)

    lend = len(prepared_df)
    prepared_df['hcc'] = [None] * lend
    prepared_df['lcc'] = [None] * lend
    for i in range(4, lend-1):
        if isHCC(prepared_df, i) > 0:
            prepared_df.at[i, 'hcc'] = prepared_df['close'][i]
        if isLCC(prepared_df, i) > 0:
            prepared_df.at[i, 'lcc'] = prepared_df['close'][i]






    # Тестова стратегія
    #________________________________________________________________________________________________
    deal = 0
    position = 0
    eth_proffit_array = [[20, 1], [40, 1], [60, 2], [80, 2], [100, 2], [150, 1], [200, 1], [200, 0]]

    prepared_df['deal_o'] = [None] * lend  #open
    prepared_df['deal_c'] = [None] * lend  #close
    prepared_df['earn'] = [None] * lend    #earn


    for i in range(4, lend-1):
        prepared_df.at[i, 'earn'] = deal
        if position > 0:                               #if open position which contract > 0 = Long
            #long
            if prepared_df['close'][i] < stop_prise:   # if actual price < stop price
                #stop_loss
                deal = deal - (open_price-prepared_df['close'][i]) # added loss to deal
                position = 0                                       # clossed position
                prepared_df.at[i, 'deal_c'] = prepared_df['close'][i] # write in deal_close actual price
            else:
                temp_arr = copy.copy(proffit_array)
                for j in range(0, len(temp_arr) - 1):
                    delta = temp_arr[j][0]
                    contracts = temp_arr[j][1]
                    if prepared_df['close'][i] > open_price + delta:
                        prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                        position = position - contracts
                        deal = deal + (prepared_df['close'][i] - open_price)*contracts
                        del proffit_array[0]

        elif position < 0:
            #short
            if prepared_df['close'][i] > stop_prise:
                #stop loss
                deal = deal - prepared_df['close'][i] - open_price
                position = 0
                prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
            else:
                temp_arr = copy.copy(proffit_array)
                for j in range(0, len(temp_arr)-1):
                    delta = temp_arr[j][0]
                    contracts = temp_arr[j][1]
                    if prepared_df['close'][i] < open_price - delta:
                        prepared_df.at[i, 'deal_c'] = prepared_df['close'][i]
                        position = position + contracts
                        deal = deal + (open_price - prepared_df['close'][i]) * contracts
                        del proffit_array[0]
        else:
            if prepared_df['lcc'][i-1] != None:
                #Long
                if prepared_df['position_in_channel'][i-1] < 0.5:
                    if prepared_df['slope'][i-1] < -20:
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]
                        proffit_array = copy.copy(eth_proffit_array)
                        position = 10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i]*0.99
            if prepared_df['hcc'][i - 1] != None:
                # Short
                if prepared_df['position_in_channel'][i-1] > 0.5:
                    if prepared_df['slope'][i - 1] > -20:
                        prepared_df.at[i, 'deal_o'] = prepared_df['close'][i]
                        proffit_array = copy.copy(eth_proffit_array)
                        position = -10
                        open_price = prepared_df['close'][i]
                        stop_prise = prepared_df['close'][i] * 1.01

    print(prepared_df)

    # Visualization
    aa = prepared_df[0:1000]
    aa = aa.reset_index()

    labels = ['close', 'deal_o', 'deal_c'] #, 'channel_max', 'channel_min'
    labels_line = ['--', '*-', '*-', 'g-', 'r-']

    j = 0
    x = pd.DataFrame()
    y = pd.DataFrame()
    for i in labels:
        x[j] = aa['index']
        y[j] = aa[i]
        j += 1

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1)

    fig.suptitle("Deals")
    fig.set_size_inches(20, 10)

    for j in range(0, len(labels)):
        ax1.plot(x[j], y[j], labels_line[j])

    ax1.set_ylabel("Price")
    ax1.grid(True)

    ax2.plot(x[0], aa['earn'], 'g-') #EMA
    ax3.plot(x[0], aa['position_in_channel'], '.-')

    ax2.grid(True)
    ax3.grid(True)
    plt.show()

"""

if __name__ == "__main__":
    main()