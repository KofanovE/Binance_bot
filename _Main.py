import copy
import time
import random
import logging

import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
from futures_sign import send_signed_request, send_public_request
from binance import Client, ThreadedWebsocketManager, ThreadedDepthCacheManager
from cred import KEY, SECRET
import requests
from math import log10, floor


from binance_functions import *
from Indicators import *

global client

logger = logging.getLogger("_Main")
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler("bot_log.log")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.warning(f"Start program: {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")

# symbol = 'ETHUSDT'
client = Client(KEY, SECRET)

# maxposition = 0.006
balans = 16
stop_percent = 0.001  # 0.01 = 1%

pointer = str(random.randint(1000, 9999))


exchange_info = client.get_exchange_info()   # Getting list of coins ...USDT
coin_list = []
for s in exchange_info['symbols']:
    if s['symbol'][-4:] == 'USDT':
        coin_list.append(s['symbol'])
num_symbol = 0
step_percent = [0.005, 0.0075, 0.01, 0.013, 0.018, 0.025, 0.035]
# eth_proffit_array = [[6, 1], [9, 1], [12, 2], [18, 2], [24, 2], [30, 1], [40, 1], [40, 0]]
# proffit_array = copy.copy(eth_proffit_array)
trailing_flag = False


def main(step):
    global proffit_array, trailing_price, num_symbol, coin_list, step_percent, maxposition, trailing_flag, stop_percent


    try:
        # New period of main program

        if num_symbol == len(coin_list) - 1:      # Choice of coin from coins_list
            num_symbol = 0
        symbol = coin_list[num_symbol]
        logger.info(f"Coin: {symbol}")

        open_sl = ""                              # Getting empty transaction_flag, if cannot connect to binance
        position = get_opened_positions(symbol)   # Getting DF of new coin
        open_sl = position[0]
        logger.debug(f"Current position: {open_sl}")

        if trailing_flag:                        # Getting stop percent with and without trailing_stop
            stop_percent = 0.003  # 0.01 = 1%
        else:
            stop_percent = 0.001




        if open_sl == "":
            # no position

            trailing_price = 0
            trailing_flag = False
            maxposition = 0
            logger.debug(f"No open position: {num_symbol}.{symbol}")
            prt(f'{num_symbol}. {symbol}  - No open position')

            # close all stop loss orders
            check_and_close_orders(symbol)                 # ! close all opened positions. Function doesn`t work normaly

            signal = check_if_signal(symbol)               # check Long or Short signal (function from Indicators.py)
            logger.debug(f"Get signal: {symbol} {signal}")



            if signal:
                # no position, but there is a not_None signal

                current_price = get_symbol_price(symbol)
                trailing_price = current_price
                maxposition = balans / current_price
                proffit_array = [[current_price * step_percent[0], 1],
                                 [current_price * step_percent[1], 1],
                                 [current_price * step_percent[2], 2],
                                 [current_price * step_percent[3], 2],
                                 [current_price * step_percent[4], 2],
                                 [current_price * step_percent[5], 1],
                                 [current_price * step_percent[6], 1],
                                 [current_price * step_percent[6], 0]]
                print(maxposition)
                logger.info(f"Position: {maxposition}")
                logger.info(f"Proffit array: {proffit_array}")





            if signal == "long":
                prt(f'{num_symbol}. {symbol}  - Open Long')
                logger.info(f"Signal -> long: {symbol}")
                open_position(symbol, 'long', maxposition)
            elif signal == 'short':
                prt(f'{num_symbol}. {symbol}  - Open Short')
                logger.info(f"Signal -> short: {symbol}")
                open_position(symbol, 'short', maxposition)
            else:
                num_symbol += 1


        else:                                               # If position is opened
            entry_price = position[5]                       # check enter price
            current_price = get_symbol_price(symbol)        # check current price
            quantity = position[1]                          # get information about current number of opened positions
            logger.info(f"Founded open position: {num_symbol}.{symbol} : {quantity}({open_sl})")
            prt('Founded open position ' + open_sl)


            if open_sl == "long":
                if trailing_flag and current_price > trailing_price:
                    trailing_price = current_price
                    logger.debug(f"Price of trailing stop: {trailing_price}")
                stop_price = trailing_price * (1 - stop_percent)     # Found stop_price

                proffit_point = entry_price + proffit_array[0][0]
                if current_price < stop_price:
                    #stop Loss
                    logger.info(f"Long -> Stop Loss: {current_price} < {stop_price}")
                    close_position(symbol, 'long', abs(quantity))
                else:
                    temp_arr = copy.copy(proffit_array)
                    for j in range(0, len(temp_arr) - 1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]
                        if current_price > entry_price + delta:
                            #take profit
                            trailing_flag = True
                            logger.info(f"Long -> Take Profit ({abs(round(maxposition * (contracts / 10), 3))}): {current_price} > {entry_price + delta}")
                            close_position(symbol, 'long', abs(round(maxposition * (contracts / 10), 3)))
                            del proffit_array[0]


            if open_sl == "short":
                if trailing_flag and current_price < trailing_price:
                    trailing_price = current_price
                    logger.debug(f"Price of trailing stop: {trailing_price}")
                stop_price = trailing_price * (1 + stop_percent)
                proffit_point = entry_price - proffit_array[0][0]
                if current_price > stop_price:
                    # stop Loss
                    logger.info(f"Short -> Stop Loss: {current_price} > {stop_price}")
                    close_position(symbol, 'short', abs(quantity))
                else:
                    temp_arr = copy.copy(proffit_array)
                    for j in range(0, len(temp_arr) - 1):
                        delta = temp_arr[j][0]
                        contracts = temp_arr[j][1]
                        if current_price < entry_price - delta:
                            # take profit
                            trailing_flag = True
                            logger.info(f"Short -> Take Profit ({abs(round(maxposition * (contracts / 10), 3))}): {current_price} < {entry_price - delta}")
                            close_position(symbol, 'short', abs(round(maxposition * (contracts / 10), 3)))
                            del proffit_array[0]

            logger.debug(f"Entry: {entry_price}, Current: {current_price}, Stop: {stop_price}, Take: {proffit_point}")
            print(entry_price, current_price, stop_price, proffit_point)

    except:
        logger.error("Information about error: ", exc_info=True)
        prt('\n\nSomething went wrong. Continuing...')
        if not open_sl:
            num_symbol += 1



def prt(message):
    # telegram message
    print(pointer + ':   ' + message)

def round_to_1(x):
    return round(x, -int(floor(log10(abs(x)))))

starttime = time.time()
timeout = time.time() + 60 * 60 * 24 # time working boot = 24 hours
counterr = 1
trailing_price = 0


while time.time() <= timeout:
    try:
        logger.info(f"______________________________________________________________________________________________________________")
        logger.info(f"Script continue running at {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")
        prt("script continue running at "+time.strftime('%Y - %m - %d %H:%M:%S', time.localtime(time.time())))
        # trades = []                           # In futures - get opened positions
        # for i in coin_list:
        #     print(i)
        #     tickerTransactions = client.get_all_orders(symbol=i)
        #     if tickerTransactions:
        #         trades.append(tickerTransactions)
        #         print("ok: ", trades)
        #     time.sleep(0.2)




        main(counterr)
        counterr += 1
        if counterr > 5:
            counterr = 1
        time.sleep(2 - ((time.time() - starttime) % 2.0)) # 1 minute interval between each new execution
    except KeyboardInterrupt:
        logger.warning(f"KeyboardInterrupt. Stopping: {time.strftime('%d.%m.%Y  %H:%M:%S', time.localtime(time.time()))}")
        print('\n\KeyboardInterrupt. Stopping.')
        exit()






"""

    pd.set_option('display.max_columns', None)  #???????????????????????? ???????????????????????? DataFrame
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






    # ?????????????? ??????????????????
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

