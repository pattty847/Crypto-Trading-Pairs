from genericpath import isfile
from subprocess import call
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json
import pandas as pd
import pandas_ta as ta
import math

from datetime import datetime

from numpy import isin
from Treasuries import Treasuries
from utils.DoStuff import DoStuff
from Exchange import Exchange

class Graphics():
    def __init__(self, api):
        self.api = api
        self.do = DoStuff()
        self.t = Treasuries()
        self.viewport_width = 1600
        self.viewport_height = int(self.viewport_width * 0.5625) # 16:9 (9/16 ratio
        self.side_panel_width = 300

        self.sma = False
        self.ema = False

        # Checks if settings file is there if not makes it and sets default into
        if not isfile("settings.json"):
            month_ago = self.do.get_time_in_past(0, 30)
            setting_init = {"last_symbol": "BTC/USDT", "last_timeframe": "1h", "last_since": month_ago, "favorite_symbols": ["BTC/USDT", "ETH/USDT", "LINK/USDT", "SOL/USDT"]}
            self.settings = setting_init
            with open("settings.json", "w") as settings_file:
                json.dump(setting_init, settings_file)
        else:
            with open("settings.json", "r") as jsonFile:
                self.settings = json.load(jsonFile)


    def _hsv_to_rgb(self, h, s, v):
        if s == 0.0: return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = v*(1.-s), v*(1.-s*f), v*(1.-s*(1.-f)); i%=6
        if i == 0: return (255*v, 255*t, 255*p)
        if i == 1: return (255*q, 255*v, 255*p)
        if i == 2: return (255*p, 255*v, 255*t)
        if i == 3: return (255*p, 255*q, 255*v)
        if i == 4: return (255*t, 255*p, 255*v)
        if i == 5: return (255*v, 255*p, 255*q)


    def update_settings(self, x):
        self.settings.update(x)
        with open("settings.json", "w") as jsonFile:
            json.dump(self.settings, jsonFile)

    def set_symbol(self, sender, app_data, user_data):
        dpg.set_value('symbol-title', app_data)
        x = {"last_symbol":app_data}
        self.update_settings(x)

    def set_timeframe(self, sender, app_data, user_data):
        dpg.set_value('timeframe-title', app_data)
        x = {"last_timeframe":app_data}
        self.update_settings(x)

    def set_period(self, sender, app_data, user_data):
        x = {"last_timeframe":app_data}
        self.update_settings(x)

    def set_date(self, sender, app_data, user_data):
        date = self.do.get_time_in_past(days=app_data['month_day'], month=app_data['month'], year=app_data['year'])
        last_since = {"last_since":date}
        dpg.set_value('date-title', date)
        self.update_settings(last_since)

    def get_interest_rates(self, sender, app_data, user_data):
        with dpg.table(header_row=False, parent="treasury-info"):
            df = self.t.avg_interest_rates()
            for i in range(df.shape[1]):
                dpg.add_table_column(label=df.columns[i])
            for i in range(df.shape[0]):
                with dpg.table_row():
                    for j in range(df.shape[1]):
                        dpg.add_text(f"{df.iloc[i, j]}")

    def add_indicator(self, indicator):
        ohlcv = {"dates":self.dates, "opens":self.opens, "closes":self.closes, "lows":self.lows, "highs":self.highs}
        df = pd.DataFrame(ohlcv)

        if indicator == 'SMA':
            sma = ta.sma(df['closes'], 14).dropna()
            dpg.add_line_series(self.dates[-len(sma):], sma.tolist(), parent='candle-series-yaxis', tag='SMA-chart')
            

        if indicator == 'EMA':
            ema = ta.ema(df['closes'], 14).dropna()
            dpg.add_line_series(self.dates[-len(ema):], ema.tolist(), parent='candle-series-yaxis', tag='EMA-chart')


        if indicator == "RSI":
            rsi = ta.rsi(df['closes'], 20).dropna()
            dpg.add_line_series(self.dates[-len(rsi):], rsi.tolist(), parent='candle-series-yaxis', tag='RSI-chart')




    # This function will, at first, update the chart with the latest saved ticker and timeframe. 
    def update_chart_series(self, sender, app_data, user_data, dates, opens, closes, lows, highs, load_ticker, load_timeframe, update):
        if not update:
            dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
            dpg.configure_item('chart-title', label=f"Symbol:{load_ticker} | Timeframe: {load_timeframe}")
            dpg.fit_axis_data('candle-series-yaxis')
            dpg.fit_axis_data('candle-series-xaxis')
            self.update_settings({"last_symbol":load_ticker})
            self.update_settings({"last_timeframe":load_timeframe})
            print("Chart updated.'")
            return

        candles = self.api.get_candles(dpg.get_value('symbols-listbox'), dpg.get_value('timeframe-listbox'), self.settings['last_since'])
        dates, opens, closes, lows, highs = self.do.candles_to_list(candles)
        dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
        dpg.configure_item('chart-title', label=f"Symbol:{load_ticker} | Timeframe: {load_timeframe}")
        dpg.fit_axis_data('candle-series-yaxis')
        dpg.fit_axis_data('candle-series-xaxis')
        self.update_settings({"last_symbol":load_ticker})
        self.update_settings({"last_timeframe":load_timeframe})
        print("Chart updated.")
        



    def chart(self):
        with dpg.child_window(width=self.viewport_width - self.side_panel_width - 15, height=-1):
            with dpg.tab_bar():        
                with dpg.tab(label="Cadlestick"):


                    # label=f"Symbol:{dpg.get_value(ticker)} | Timeframe: {dpg.get_value(tf)}", tag='chart-title', height=-1, width=1200
                    with dpg.plot(label=f"Symbol:{self.settings['last_symbol']} | Timeframe: {self.settings['last_timeframe']}", tag='chart-title', height=-1, width=self.viewport_width - self.side_panel_width - 5):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='candle-series-xaxis', time=True)
                        with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='candle-series-yaxis'):
                            dpg.add_candle_series([], [], [], [], [], tag='candle-series', time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
                            dpg.fit_axis_data(dpg.top_container_stack())                

                with dpg.tab(tag='cointegration', label="Cointegration"):
                    with dpg.plot(label="Heat Series", no_mouse_pos=True, height=-1, width=-1):
                        dpg.add_plot_axis(dpg.mvXAxis, label="x", lock_min=True, lock_max=True, no_gridlines=True, no_tick_marks=True)
                        with dpg.plot_axis(dpg.mvYAxis, label="y", no_gridlines=True, no_tick_marks=True, lock_min=True, lock_max=True):
                            # score_matrix, pvalue_matrix, pairs = gui.do.find_cointegrated_pairs(self.api.get_matrix_of_closes(["BTC/USDT", "ETH/USDT", "LINK/USDT", "ATOM/USDT", "SUSHI/USDT"], "4h", gui.settings['last_since']), 0.05)
                            # dpg.add_heat_series(pvalue_matrix, 5, 5)
                            pass
                            

                with dpg.tab(label="Treasury Info", tag="treasury-info"):
                    dpg.add_button(label='Average Interest Rates', callback=lambda s, a, u:self.get_interest_rates(s, a, u))

                    with dpg.collapsing_header(label="Chart"):
                        with dpg.plot(label=f"Symbol: Interest Rates", tag='interest-title', height=-1, width=self.viewport_width - self.side_panel_width - 5):
                            dpg.add_plot_legend()
                            dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='interest-series-xaxis', time=True)
                            with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='interest-series-yaxis'):
                                pass

                with dpg.tab(label="Demo"):
                    dpg.add_button(label='Start Demo', callback=lambda:self.demo())
                    

    def trade(self): 
        with dpg.group():
            with dpg.child_window(autosize_x=True, height=(self.viewport_height/2), pos=[self.viewport_width - self.side_panel_width, 7]):
                with dpg.collapsing_header(label="Trade"):

                    with dpg.group(horizontal=True):
                        dpg.add_text(default_value=self.settings['last_symbol'], tag='symbol-title')
                        dpg.add_text(default_value=self.settings['last_timeframe'], tag='timeframe-title')
                        dpg.add_text(default_value=self.settings['last_since'], tag='date-title')

                    with dpg.tree_node(label="Favorites"):
                        with dpg.group(horizontal=True):
                            dpg.add_listbox(self.settings['favorite_symbols'], tag='favorite-symbols-listbox', default_value=self.settings['favorite_symbols'][0], width=-1, callback=self.set_symbol, num_items=int(len(self.settings['favorite_symbols']) * 0.33))

                    with dpg.tree_node(label="Symbol"):
                        with dpg.group(horizontal=False):
                            # dpg.add_text("Filter usage:\n"
                            # "  \"\"               display all lines\n"
                            # "  \"xxx\"         display lines containing \"xxx\"\n"
                            # "  \"xxx,yyy\"  display lines containing \"xxx\" or \"yyy\"\n"
                            # "  \"-xxx\"        hide lines containing \"xxx\"")
                            dpg.add_input_text(label="Search", filter_key='symbols-filter', callback=lambda s, a: dpg.set_value("symbols-filter", a))
                            with dpg.filter_set(tag="symbols-filter"):
                                dpg.add_listbox(self.api.symbols, filter_key='symbols-filter', tag='symbols-listbox', default_value=self.settings['last_symbol'], width=-1, callback=self.set_symbol, num_items=50)


                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            dpg.add_text("Timeframe")
                            dpg.add_listbox(self.api.timeframes, tag='timeframe-listbox', default_value=self.settings['last_timeframe'], width=75, callback=self.set_timeframe, num_items=9)
                        with dpg.group(horizontal=False):
                            from_ = dpg.add_text("From", color=[0, 255, 0])
                            with dpg.tooltip(from_):
                                dpg.add_text("The calendar shows today's date. The date at the top shows the start of the chart.")
                            date = datetime.today().strftime('%Y-%m-%d').split("-")
                            year = str(int(date[0][2:]))
                            year_ = f'1{year}'
                            dates = {'month_day': int(date[2]), 'year':int(year_), 'month':int(date[1])}
                            
                            dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day, label='From', default_value=dates, callback=self.set_date)
                

                # Build the chart from the last saved ticker and timeframe
                candles = self.api.get_candles(self.settings['last_symbol'], self.settings['last_timeframe'], self.settings['last_since'])
                self.dates, self.opens, self.closes, self.lows, self.highs = self.do.candles_to_list(candles)
                self.update_chart_series(None, None, None, self.dates, self.opens, self.closes, self.lows, self.highs, self.settings['last_symbol'], self.settings['last_timeframe'], False)

                dpg.add_separator()

                # This button will update the chart when the user clicks it. 
                dpg.add_button(label="Go", width=-1, callback=lambda a, s, u: self.update_chart_series(a, s, u, None, None, None, None, None, dpg.get_value('symbols-listbox'), dpg.get_value('timeframe-listbox'), True))
                

                
                with dpg.group(horizontal=True):
                    # step will need to equal exchange min order size
                    dpg.add_input_float(tag='limit-price', label="Limit Price", width=115, step=0, step_fast=0, callback=lambda:print(dpg.get_value('limit-price')), format="%.04f")
                
                with dpg.group(horizontal=True):
                    dpg.add_button(tag='limit', label="Limit", width=115)
                    # dpg.add_theme_color("limit", self._hsv_to_rgb(2/7.0, 0.6, 0.6))
                    dpg.add_button(label="Market", width=-1)


        with dpg.child_window(autosize_x=True, height=-1, pos=[self.viewport_width - self.side_panel_width, self.viewport_height/2+5]):
            with dpg.collapsing_header(label="Indicators"):
                with dpg.group(horizontal=True):
                    dpg.add_button(label="SMA", width=75, callback=lambda:self.add_indicator("SMA"))
                    dpg.add_button(label="EMA", width=75, callback=lambda:self.add_indicator("EMA"))
                    dpg.add_button(label="RSI", width=75, callback=lambda:self.add_indicator("RSI"))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("SMA-chart"), tag='sma-del')
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("EMA-chart"), tag='ema-del')
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("RSI-chart"), tag='rsi-del')
                with dpg.group(horizontal=True):
                    dpg.add_button(label="MACD", width=75, callback=lambda:self.add_indicator("MACD"))
                    dpg.add_button(label="STOCH", width=75, callback=lambda:self.add_indicator("STOCH"))
                    dpg.add_button(label="MFI", width=75, callback=lambda:self.add_indicator("MFI"))
                with dpg.group(horizontal=True):
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("MACD-chart"), tag='macd-del')
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("STOCH-chart"), tag='stoch-del')
                    dpg.add_button(label="Delete", width=75, callback=lambda:dpg.delete_item("MFI-chart"), tag='mfi-del')
            with dpg.collapsing_header(label="Settings"):
                with dpg.group(horizontal=False):
                    dpg.add_button(label="Gui Settings", width=-1, callback=lambda a, s, u: dpg.show_style_editor())
                    dpg.add_button(label="Gui Settings", width=-1, callback=lambda a, s, u: dpg.show_style_editor())
                    dpg.add_button(label="Gui Settings", width=-1, callback=lambda a, s, u: dpg.show_style_editor())
            


    def set_up(self):
        # This is the first step to use the dearpygui library.
        dpg.create_context()

        with dpg.window(tag="Main", no_resize=True, no_scrollbar=True):
            self.chart()
            self.trade()


        dpg.create_viewport(title='Custom Title', width=self.viewport_width, height=self.viewport_height, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Main", True)
        dpg.start_dearpygui()

        dpg.destroy_context()


    def demo(self):
        demo.show_demo()

ftx = Exchange("ftx")
gui = Graphics(ftx)
gui.set_up()