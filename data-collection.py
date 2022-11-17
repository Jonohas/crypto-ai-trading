import requests
import json
import time
from os.path import exists
import tqdm
import shutil
import os
import queue
from threading import Thread

base_url = "https://api.binance.com"

wanted_symbols = ["VET"]

request_limit = 1200
request_queue = queue.Queue()
write_queue = queue.Queue()

request_pbar = None
coins_pbar = None

def get_server_time():
    endpoint = "/api/v3/exchangeInfo"

    # params
    url = base_url + endpoint
    response = requests.get(url)

    # save data to json file
    with open("exchangeInfo.json", "w") as f:
        string = json.dumps(response.json(), indent=4)
        f.write(string)

def convert_candlestick_array_to_csv(candlestick_array, file_exists):
    # convert array to csv
    csv = ""
    if not file_exists:
        csv += "event_time,open,close,high,low,volume\n"
    
    for candlestick in candlestick_array:
        event_time = candlestick[0]
        open_price = candlestick[1]
        close_price = candlestick[4]
        high_price = candlestick[2]
        low_price = candlestick[3]
        volume = candlestick[5]
        csv += f"{event_time},{open_price},{close_price},{high_price},{low_price},{volume}\n"

    return csv

def write_data():
    global write_queue

    while True:
        write_object = write_queue.get()
        symbol = write_object["symbol"]
        data = write_object["data"]

        file_name = f"Data/raw/{symbol}.csv"
        # save data to json file
        if exists(file_name):
            with open(file_name, "a") as f:
                csv = convert_candlestick_array_to_csv(data, True)
                f.write(csv)
        else:
            with open(file_name, "w") as f:
                csv = convert_candlestick_array_to_csv(data, False)
                f.write(csv)

def get_candlestick_data():
    global request_queue, request_limit, request_pbar
    

    while not request_queue.empty():
        
        params = request_queue.get()
        endpoint = "/api/v3/klines"
        url = base_url + endpoint
        response = requests.get(url, params=params['params'])
        request_pbar.set_description_str(f"Requesting {params['symbol']}, Used weight: {response.headers['X-MBX-USED-WEIGHT-1M']}")
        data = response.json()

        write_queue.put({
            "symbol": params['symbol'],
            "data": data
        })

        request_pbar.update(1)

def get_symbols():
    endpoint = "/api/v3/exchangeInfo"
    url = base_url + endpoint
    response = requests.get(url)
    
    string = json.dumps(response.json())
    obj = json.loads(string)
    symbols = [symbol["symbol"] for symbol in obj["symbols"]]

    symbols = [symbol for symbol in symbols if symbol[-3:] == wanted_symbols[0] or symbol.startswith(wanted_symbols[0])]

    return symbols

def clean_up():
    shutil.rmtree('Data/raw')
    os.mkdir('Data/raw')
    

if __name__ == "__main__":
    request_queue = queue.Queue()
    clean_up()

    
    symbols = get_symbols()

    symbol_count = 0
    total_symbols = len(symbols)


    requester0 = Thread(target=get_candlestick_data)
    requester1 = Thread(target=get_candlestick_data)
    requester2 = Thread(target=get_candlestick_data)
    requester3 = Thread(target=get_candlestick_data)
    requester4 = Thread(target=get_candlestick_data)

    writer0 = Thread(target=write_data)
    writer1 = Thread(target=write_data)
    writer2 = Thread(target=write_data)
    writer3 = Thread(target=write_data)
    writer4 = Thread(target=write_data)

    print(f"Requesting following symbols: {symbols}")




    for symbol in symbols:
        symbol_count += 1
        end_time = int(time.time() * 1000)
        # start_time 1 year ago
        start_time = end_time - (365 * 24 * 60 * 60 * 1000)

        difference = (end_time - start_time) / (1000 * 60)

        batch_size = 1000
        batch_count = int(difference / batch_size) + 1

        requests_params = []
         
        for i in range(batch_count):
            #  (batch_bar := tqdm.tqdm(, position=1))
            # batch_bar.set_description(f"<{symbol}> {i} of {batch_count}, items left: {items_left}")

            start = start_time + (i * batch_size * 1000 * 60)
            # calculate items left to fetch
            items_left = int(difference - (i * batch_size))

            params = {
                "symbol": symbol,
                "interval": "1m",
                "startTime": start,
                "endTime": end_time,
                "limit": items_left
            }
            requests_params.append(params)

            request_object = {
                "symbol": symbol,
                "params": params
            }
            request_queue.put(request_object)



    request_pbar = tqdm.tqdm(total=request_queue.qsize(), position=1)
    # coins_pbar = tqdm.tqdm(total=total_symbols, position=0)

    requester0.start()
    requester1.start()
    requester2.start()
    requester3.start()
    requester4.start()
    
    writer0.start()
    writer1.start()
    writer2.start()
    writer3.start()
    writer4.start()

    requester0.join()
    requester1.join()
    requester2.join()
    requester3.join()
    requester4.join()

    writer0.join()
    writer1.join()
    writer2.join()
    writer3.join()
    writer4.join()
    
