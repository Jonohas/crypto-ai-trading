import tkinter as tk
from CryptoEnvironment import CryptoEnvironment as CryptoEnv
import pandas as pd
from ActionSpace import ActionSpace
import random

df = pd.read_csv('../Data/dataset/VETUSDT.csv')
training_data = df.drop(['original_open', 'original_close', 'original_high', 'original_low', 'original_volume', 'event_time'], axis=1)

arguments={
    'risk':  0.2,
    'initial_balance':  100,
    'initial_coin_amount':  0,
    'sequence_length':  100,
    'look_back_window':  10,
    'look_ahead_window':  10,
    'profitable_sell_threshhold':  1,
    'profitable_sell_reward':  1,
    'step_limit': 400,
    'consecutive_threshold': 10,
    'fee': 0.006
}

input_shape = (arguments['sequence_length'], df.shape[1] + 2)
env = CryptoEnv(df, training_data=training_data, arguments=arguments, input_shape=input_shape, log_dir='./logs', verbose=False, render=True)

def create_dataset():
    # create csv file to store dataset
    with open('../Data/dataset/VETUSDT_labelled.csv', 'w+') as f:
        f.write('event_time,open,close,high,low,volume,original_open,original_close,original_high,original_low,original_volume,adosc,atr,bb_upper,bb_middle,bb_lower,macd,macd_signal,macd_hist,mfi,rsi,sar,tema,action' + '\n')

def append_to_dataset(sample):
    with open('../Data/dataset/VETUSDT_labelled.csv', 'a') as f:
        f.write(f"{sample['event_time']},{sample['open']},{sample['close']},{sample['high']},{sample['low']},{sample['volume']},{sample['original_open']},{sample['original_close']},{sample['original_high']},{sample['original_low']},{sample['original_volume']},{sample['adosc']},{sample['atr']},{sample['bb_upper']},{sample['bb_middle']},{sample['bb_lower']},{sample['macd']},{sample['macd_signal']},{sample['macd_hist']},{sample['mfi']},{sample['rsi']},{sample['sar']},{sample['tema']},{sample['action']}" + '\n')


create_dataset()
env.reset()
env.render(0)

def buy():
    action = 0
    observation, reward, done, info = env.step(action, False)
    state = env._get_state(env._tick)
    state['action'] = action

    append_to_dataset(state)
    env.render(0)

def hold():
    action = 1
    observation, reward, done, info = env.step(action, False)
    state = env._get_state(env._tick)
    state['action'] = action
    append_to_dataset(state)
    env.render(0)

def sell():
    action = 2
    observation, reward, done, info = env.step(action, False)
    state = env._get_state(env._tick)
    state['action'] = action
    append_to_dataset(state)
    env.render(0)


## create window to show the graph
window = tk.Tk()
window.title('Label Data')
window.geometry('800x600')
window.configure(background='white')
## create a canvas that can fit the above window
canvas = tk.Canvas(window, width = 800, height = 600)
canvas.pack()

## create a frame
frame = tk.Frame(window)
frame.place(relx=0.5, rely=0.1, relwidth=0.75, relheight=0.1, anchor='n')

## create a frame for 3 buttons: buy, hold, sell
button_frame = tk.Frame(window)
button_frame.place(relx=0.5, rely=0.8, relwidth=0.75, relheight=0.1, anchor='n')

## create a button, say buy
button_buy = tk.Button(button_frame, text='Buy', bg='green', fg='white', command=buy)
button_buy.place(relx=0.1, rely=0.1, relwidth=0.2, relheight=0.8)

## create a button, say hold
button_hold = tk.Button(button_frame, text='Hold', bg='yellow', fg='black', command=hold)
button_hold.place(relx=0.4, rely=0.1, relwidth=0.2, relheight=0.8)

## create a button, say sell
button_sell = tk.Button(button_frame, text='Sell', bg='red', fg='white', command=sell)
button_sell.place(relx=0.7, rely=0.1, relwidth=0.2, relheight=0.8)




window.mainloop()