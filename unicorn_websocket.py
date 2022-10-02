from unicorn_binance_websocket_api.manager import BinanceWebSocketApiManager

import time
import threading
import pandas as pd
import ccxt
import matplotlib.pyplot as plt

def print_stream_data_from_stream_buffer(binance_websocket_api_manager):
    while True:
        if binance_websocket_api_manager.is_manager_stopping():
            exit(0)
        oldest_stream_data_from_stream_buffer = binance_websocket_api_manager.pop_stream_data_from_stream_buffer()
        if oldest_stream_data_from_stream_buffer is False:
            time.sleep(0.01)
        else:
            try:
                print(oldest_stream_data_from_stream_buffer)
            except Exception:
                # not able to process the data? write it back to the stream_buffer
                binance_websocket_api_manager.add_to_stream_buffer(oldest_stream_data_from_stream_buffer)

if __name__ == '__main__':
    # First we create a BinanceWebSocketApiManager object Binance exchange
    binance_websocket_api_manager = BinanceWebSocketApiManager(exchange="binance.com")

    # Create a worker thread whose output is the callback print_stream_data_from_stream_buffer, the args are the Socket Object
    worker_thread = threading.Thread(target=print_stream_data_from_stream_buffer, args=(binance_websocket_api_manager,))

    # Start
    worker_thread.start()

    # Assign lists of stream types and tickers
    kline_stream_id = binance_websocket_api_manager.create_stream(['kline_1d'], ['btcusdt'])

    # Once the main thread has started your threads, there's nothing else for it to do. So it exits, and the threads are destroyed instantly. 
    # So let's keep the main thread alive.
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nStopping ... just wait a few seconds!")
        binance_websocket_api_manager.stop_manager_with_all_streams()