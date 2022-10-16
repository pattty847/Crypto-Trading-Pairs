from genericpath import isfile
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json

from datetime import datetime

from numpy import isin
from utils.DoStuff import DoStuff
from Exchange import Exchange

class Graphics():
    def __init__(self, api):
        self.api = api
        self.do = DoStuff()
        self.tf = '1d'
        self.viewport_width = 1600
        self.viewport_height = 900

        self.last_symbol = None

        # TODO: Check if settings file is not created yet and if not make one with default settings.
        if not isfile("settings.json"):
            #                                                                      use do.gettimepast function
            format = {"last_ticker": "BTC/USDT", "last_timeframe": "1h", "last_since": "2022-10-01T19:00:00.000Z"}
            
        with open("settings.json", "r") as jsonFile:
            self.settings = json.load(jsonFile)


    def update_settings(self, x):
        self.settings.update(x)
        with open("settings.json", "w") as jsonFile:
            json.dump(self.settings, jsonFile)


    def set_ticker(self, sender, app_data, user_data):
        dpg.configure_item('ticker-listbox', label = app_data)
        x = {"last_ticker":app_data}
        self.update_settings(x)



    def set_timeframe(self, sender, app_data, user_data):
        dpg.configure_item('timeframe-listbox', label = app_data)
        x = {"last_timeframe":app_data}
        self.update_settings(x)



    def set_date(self, sender, app_data, user_data):
        print(app_data)
        self.update_settings({"last_since":self.do.get_time_in_past(minutes=0, days=app_data['month_day'])})



    def set_trade_price(self, sender, app_data, user_data):
        print(app_data)


    
    def update_old_candle(self, dates, opens, closes, highs, lows):
        dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.convert_timeframe(self.settings['last_timeframe']))
        dpg.configure_item('chart-title', label=f"Symbol:{self.settings['last_ticker']} | Timeframe: {self.settings['last_timeframe']}")
        dpg.fit_axis_data('candle-series-yaxis')
        dpg.fit_axis_data('candle-series-xaxis')



    def refresh_chart(self, sender, app_data, user_data):
        # Loading indicator start stop at end
        # dpg.set_value('loading-symbol', show=True)
        (dates, opens, highs, closes, lows) = self.get_candles()
        dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.convert_timeframe(self.settings['last_timeframe']))
        dpg.configure_item('chart-title', label=f"Symbol:{self.settings['last_ticker']} | Timeframe: {self.settings['last_timeframe']}")
        dpg.fit_axis_data('candle-series-yaxis')
        dpg.fit_axis_data('candle-series-xaxis')
        # dpg.set_value('loading-symbol', show=False)



    def get_candles(self):
        # By this function call the settings for each of these vars should be initialized and not empty.
        load_ticker = self.settings["last_ticker"]
        load_timeframe = self.settings["last_timeframe"]
        load_since = self.settings["last_since"]
        print(f'Loading : [ticker: {load_ticker} | timeframe: {load_timeframe} | Since: {load_since}]')
        df = self.api.get_candles(load_ticker, load_timeframe, load_since)
        if isinstance(df, tuple):
            return df

        dates = list(df['date']/1000)
        opens = list(df['open'])
        closes = list(df['close'])
        lows = list(df['low'])
        highs = list(df['high'])

        return (dates, opens, highs, closes, lows)



    # TODO: Start using lambda functions: callback = lambda:dpg.configure_item("tag", show=True, pos=[x, y], etc)

    def charts_window(self, sender, app_data, user_data):
        # Each window is a subset inside the main viewport window.
        # To set this window to fill the viewport add this parameter: tag="name" 
        # Set the primary window at bottom: dpg.set_primary_window("name", True)
        with dpg.window(label=f"{self.api.name}", width=self.viewport_width - 25, height=self.viewport_height - 75, pos=[5, 25], no_move=True, no_resize=True, no_scrollbar=True):

            with dpg.menu_bar():

                if self.api.api.has['fetchOHLCV']:
                    
                    # TODO: Finish this
                    # with dpg.menu(label="Exchange"):
                    #     dpg.add_listbox(self.api.symbols, callback = self.callback)
                    # Set default values to last ticker, timeframe, and date that was open.


                    with dpg.menu(label="Ticker"):
                        # Default value checks for ticker stored in settings which is stored before user closes the program. 
                        ticker = dpg.add_listbox(self.api.symbols, tag='ticker-listbox', num_items = 20, callback = self.set_ticker, default_value=self.settings['last_ticker'] if self.settings['last_ticker'] != "" else "BTC/USDT", label=f"({self.settings['last_ticker']})")

                    with dpg.menu(label="Timeframe"):
                        tf = dpg.add_listbox(self.api.timeframes, tag='timeframe-listbox', num_items = 10, width=50, callback = self.set_timeframe, default_value=self.settings['last_timeframe'], label=f"({self.settings['last_timeframe']})")

                    with dpg.menu(label="Date"):
                        date = datetime.today().strftime('%Y-%m-%d').split("-")
                        year = str(int(date[0][2:]))
                        year_ = f'1{year}'
                        dates = {'month_day': int(date[2]), 'year':int(year_), 'month':int(date[1])}
                        
                        dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day, label='From', default_value=dates, callback=self.set_date)

                    dpg.add_button(label='Go', callback=self.refresh_chart)


                else:

                    dpg.add_text(f'{self.api.name} does not have candlesticks available.')
                    return
                    
            (dates, opens, highs, closes, lows) = self.get_candles()


            with dpg.group(horizontal=True):
                with dpg.plot(label=f"Symbol:{dpg.get_value(ticker)} | Timeframe: {dpg.get_value(tf)}", tag='chart-title', height=-1, width=1200):
                    dpg.add_plot_legend()
                    xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='candle-series-xaxis', time=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='candle-series-yaxis'):
                        dpg.add_candle_series(dates, opens, closes, lows, highs, tag='candle-series', time_unit=self.convert_timeframe(dpg.get_value(tf)))
                        dpg.fit_axis_data(dpg.top_container_stack())
                        
                        # TODO: Create way to add indicators
                        # dpg.add_line_series(dates, closes)
                    dpg.fit_axis_data(xaxis)



                with dpg.group(horizontal=False):
                    with dpg.collapsing_header(label="Trade", pos=[1215, 50]):
                        with dpg.tree_node(label="Place Order"):
                            with dpg.group():
                                dpg.add_input_float(label="input float", default_value=closes[-1], callback=self.set_trade_price, format="%.06f", width=-1)

                            # with dpg.tree_node(label="Basic"):
                            with dpg.table(header_row=False, borders_innerH=True, 
                                    borders_outerH=True, borders_innerV=True, 
                                    borders_outerV=True, width=-1):
                            
                                # Add two columsn
                                dpg.add_table_column()
                                dpg.add_table_column()

                                with dpg.table_row(height=50):
                                    dpg.add_button(label='Buy', height=48, width=-1)
                                    dpg.add_button(label='Sell', height=48, width=-1)
                                
                            with dpg.table(header_row=False, borders_innerH=True, 
                                    borders_outerH=True, borders_innerV=True, 
                                    borders_outerV=True, width=-1):

                                dpg.add_table_column()

                                with dpg.table_row(height=50):
                                    dpg.add_button(label='Cancel', height=48, width=-1)

                        with dpg.tree_node(label="Indicator"):
                            with dpg.group(horizontal=True):
                                dpg.add_selectable(label='SMA', width=100)
                                dpg.add_selectable(label='EMA', width=100)
                                dpg.add_selectable(label='MACD', width=100)
                            with dpg.group(horizontal=True):
                                dpg.add_selectable(label='MACD', width=100)
                                dpg.add_selectable(label='Wavetrend', width=100)
                                dpg.add_selectable(label='RSI', width=100)
            



    def cointegration(self, sender, app_data, user_data):
        with dpg.window(label=f"Cointegration Heatmap", width=self.viewport_width - 25, height=self.viewport_height - 75, pos=[5, 25], no_move=True, no_resize=True, no_close=True):
            with dpg.plot(label="Heat Series", no_mouse_pos=True, height=-1, width=-1):
                dpg.add_plot_axis(dpg.mvXAxis, label="x", lock_min=True, lock_max=True, no_gridlines=True, no_tick_marks=True)
                with dpg.plot_axis(dpg.mvYAxis, label="y", no_gridlines=True, no_tick_marks=True, lock_min=True, lock_max=True):
                    score_matrix, pvalue_matrix, pairs = gui.do.find_cointegrated_pairs(api.get_matrix_of_closes(["BTC/USDT", "ETH/USDT", "LINK/USDT"], "4h", gui.settings['last_since']), 0.05)
                    dpg.add_heat_series(pvalue_matrix, 3, 3)



    def run(self):
        # This is the first step to use the dearpygui library.
        dpg.create_context()

        # This is our primary viewport window which we have a menu bar at the top with other window selections.
        with dpg.window(tag="Main", no_resize=True, no_scrollbar=True):
            with dpg.menu_bar():
                with dpg.menu(label='Charts'):
                    dpg.add_button(label="Open", callback=self.charts_window)

                with dpg.menu(label='Demo'):
                    dpg.add_button(label="Open", callback=self.demo)

                with dpg.menu(label="Cointegration"):
                    dpg.add_button(label="Open", callback=self.cointegration)

        dpg.create_viewport(title='Custom Title', width=self.viewport_width, height=self.viewport_height, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Main", True)
        dpg.start_dearpygui()

        # below replaces, start_dearpygui()
        # while dpg.is_dearpygui_running():
        #     # insert here any code you would like to run in the render loop
        #     # you can manually stop by using stop_dearpygui()
        #     print("this will run every frame")
        #     dpg.render_dearpygui_frame()

        dpg.destroy_context()



    def demo(self):
        demo.show_demo()

api = Exchange("ftx")
gui = Graphics(api)
gui.run()
