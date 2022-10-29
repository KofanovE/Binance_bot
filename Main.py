import numpy as np
import pandas as pd
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib as mpl
"""
В PrepareDF функції планується добавити стовпці мін та макс каналу з середніх значеннь з історії, 
позиція в каналі та кут нахилу тренду
"""
def main():
    api_key = 'LSZH501HZPZVU1GA'
    interval_var = '15min'
    symbol = 'BTC'

    url = f'https://www.alphavantage.co/query?function=CRYPTO_INTRADAY&symbol={symbol}&market=USD&interval={interval_var}&apikey={api_key}&datatype=csv&outputsize=full'
    df = pd.read_csv(url)
    df = df[::-1]                                       # [timestamp, open, high, low, close, volume]
    #frame = pd.DataFrame(df[['high', 'low', 'close']])  # Тестовий датафрейм
    #print(df)
    #print(frame)
    #frame[['high', 'low']].plot()
    #plt.show()
    PrepareDF(df)




def PrepareDF(DF):                                                     # Функція формування повного датафрейму
    ohlc = DF
    ohlc.columns = ["date", "open", "high", "low", "close", "volume"]  # Зміна назв колонок датафрейму
    ohlc = ohlc.set_index('date')
    print(ohlc)




if __name__ == "__main__":
    main()