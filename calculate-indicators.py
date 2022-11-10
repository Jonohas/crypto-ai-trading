import pandas as pd
import os
import talib as tb
import numpy as np
import time
import tqdm
import threading
from sklearn import preprocessing
from numba import jit

@jit
def calc(value1, value2):
    if value1 == 0:
        return 0
    return (value2 - value1) / value1

@jit
def calculate_indicators(df, pbar, filename):
    pbar.set_description_str(f"Calculating indicators for {filename}")

    o = df['open'].values
    c = df['close'].values
    h = df['high'].values
    l = df['low'].values
    v = df['volume'].values

    df['adosc'] = tb.ADOSC(h, l, c, v, fastperiod=3, slowperiod=10)
    df['atr'] = tb.ATR(h, l, c, timeperiod=14)

    df['bb_upper'], \
    df['bb_middel'], \
    df['bb_lower'] = tb.BBANDS(c, timeperiod=5)

    df['macd'], \
    df['macd_signal'], \
    df['macd_hist'] = tb.MACD(c, fastperiod=12, slowperiod=26, signalperiod=9)
    df['mfi'] = tb.MFI(h, l, c, v, timeperiod=14)
    df['rsi'] = tb.RSI(c, timeperiod=14)
    df['sar'] = tb.SAR(h, l, acceleration=0.02, maximum=0.2)
    df['tema'] = tb.TEMA(c, timeperiod=30)

@jit
def calculate_difference_percentage(df):
    first_candle = df.iloc[0]
    second_candle = df.iloc[1]

    second_candle['open_diff'] = calc(second_candle['open'], first_candle['open'])
    second_candle['close_diff'] = calc(second_candle['close'], first_candle['close'])
    second_candle['high_diff'] = calc(second_candle['high'], first_candle['high'])
    second_candle['low_diff'] = calc(second_candle['low'], first_candle['low'])
    second_candle['volume_diff'] = calc(second_candle['volume'], first_candle['volume'])


    print("open v1: {} v2: {} diff: {}".format(first_candle["open"], second_candle["open"], second_candle['open_diff']))
    # print("close v1: {} v2: {} diff: {}".format(first_candle["close"], second_candle["close"], second_candle['close_diff']))
    # print("high v1: {} v2: {} diff: {}".format(first_candle["high"], second_candle["high"], second_candle['high_diff']))
    # print("low v1: {} v2: {} diff: {}".format(first_candle["low"], second_candle["low"], second_candle['low_diff']))
    # print("volume v1: {} v2: {} diff: {}".format(first_candle["volume"], second_candle["volume"], second_candle['volume_diff']))

@jit
def normalize(value, pbar, filename, total_length, df):
    if value.name < total_length:
            
        current_candle = df.iloc[value.name]
        previous_candle = df.iloc[value.name - 1]

        pbar.set_description_str(f"Normalizing {filename}, {value.name}/{total_length}, {round(value.name/total_length*100)}%")

        value["open"] = calc(previous_candle["open"], current_candle["open"])
        value["close"] = calc(previous_candle["close"], current_candle["close"])
        value["high"] = calc(previous_candle["high"], current_candle["high"])
        value["low"] = calc(previous_candle["low"], current_candle["low"])
        value["volume"] = calc(previous_candle["volume"], current_candle["volume"])

        value["adosc"] = calc(previous_candle["adosc"], current_candle["adosc"])
        value["atr"] = calc(previous_candle["atr"], current_candle["atr"])

        value["bb_upper"] = calc(previous_candle["bb_upper"], current_candle["bb_upper"])
        value["bb_middel"] = calc(previous_candle["bb_middel"], current_candle["bb_middel"])
        value["bb_lower"] = calc(previous_candle["bb_lower"], current_candle["bb_lower"])

        value["macd"] = calc(previous_candle["macd"], current_candle["macd"])

        value["mfi"] /= 100
        value["rsi"] /= 100

        value["sar"] = calc(previous_candle["sar"], current_candle["sar"])
        value["tema"] = calc(previous_candle["tema"], current_candle["tema"])

    pbar.update(1)
    



def thread_tast(file_location, file_destination):
    filename = file_location.split("/")[-1]
    df = pd.read_csv(file_location)

    pbar = tqdm.tqdm(total=df.shape[0])

    calculate_indicators(df, pbar, filename)
    df.dropna(inplace=True)

    df_original = df.copy()

    df.apply(normalize, axis=1, args=(pbar, filename, df.shape[0], df_original))

    df.dropna(inplace=True)
    df.to_csv(file_destination, index=False)



for file in os.listdir('Data/raw'):
    file_location = f"Data/raw/{file}"
    file_destination = f"Data/dataset/{file}"

    t = threading.Thread(target=thread_tast, args=(file_location, file_destination))
    t.start()


    # df = pd.read_csv('Data/raw/' + file)

    # calculate_indicators(df, pbar, file)
    # df.dropna(inplace=True)

    # df_original = df.copy()

    # df.apply(normalize, axis=1, args=(pbar, file, df.shape[0], df_original))
    # # df_test = df.copy()


    # # event_times = pd.DataFrame(df['event_time'].values, columns=['event_time'])
    # # df.drop(columns=['event_time'], inplace=True)
    
    # # norm = df.pct_change(axis=0, )

    # # df['event_time'] = event_times
    # # df.index = df['event_time']

    # # calculate_difference_percentage(df_test)
    # # first_candle = norm.iloc[0]
    # # second_candle = norm.iloc[1]
    # # print("open v1: {} v2: {}".format(first_candle["open"], second_candle["open"]))


    # df.dropna(inplace=True)
    # df.to_csv('Data/dataset/' + file, index=False)
    # pbar.update(1)

