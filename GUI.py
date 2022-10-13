from cProfile import label
from string import hexdigits
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

from utils.DoStuff import DoStuff
from Exchange import Exchange

class Graphics():
    def __init__(self, api):
        self.api = api
        self.do = DoStuff()
        self.tf = '1d'
        self.viewport_width = 1200
        self.viewport_height = 900


    def callback(self, sender, app_data, user_data):
        print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")

        # TODO: This will need to pull whatever data, if any, up to a certain amount of time which needs to be
        # thought of. Idk looks like tradingview shows up to 30 days but maybe that was my last frame width saved.
        # 30 days sounds good tho
        df = self.api.get_candles(app_data, self.tf, self.do.get_time_in_past(0, 30))

        dates = list(df['date']/1000)
        opens = list(df['open'])
        closes = list(df['close'])
        lows = list(df['low'])
        highs = list(df['high'])


        with dpg.window(label='Ticker', width=600, height=500):
            dpg.add_text(f"Timeframe: {self.tf} | Symbol:{app_data}")
            with dpg.plot(label="Candle Series", height=400, width=-1):
                dpg.add_plot_legend()
                xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="Day", time=True)
                with dpg.plot_axis(dpg.mvYAxis, label="USD"):
                    dpg.add_candle_series(dates, opens, closes, lows, highs, label=app_data, time_unit=dpg.mvTimeUnit_Day)
                    dpg.fit_axis_data(dpg.top_container_stack())
                dpg.fit_axis_data(xaxis)


    def set_timeframe(self, sender, app_data, user_data):
        self.tf = app_data


    def run(self):
        # This is the first step to use the dearpygui library.
        dpg.create_context()

        # Each window is a subset inside the main viewport window.
        # To set this window to fill the viewport add this parameter: tag="name" 
        # Set the primary window at bottom: dpg.set_primary_window("name", True)
        with dpg.window(tag="Main"):
            with dpg.menu_bar():
                with dpg.menu(label="Charts"):
                    with dpg.menu(label="Ticker"):
                        dpg.add_listbox(self.api.symbols, callback = self.callback)
                    with dpg.menu(label="Timeframe"):
                        # dpg.add_listbox(self.api.timeframes.keys(), label='Timeframe', callback = self.set_timeframe)
                        dpg.add_listbox(self.api.timeframes, callback = self.set_timeframe, label=f"({self.tf})")
            dpg.add_listbox(self.api.symbols, callback = self.callback, width=200, pos=[self.viewport_width - 225, 25])

        dpg.create_viewport(title='Custom Title', width=self.viewport_width, height=self.viewport_height)
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
        dpg.create_context()
        dpg.create_viewport(title='Custom Title', width=self.viewport_width, height=self.viewport_height)

        demo.show_demo()

        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

api = Exchange("ftx")
gui = Graphics(api)
gui.run()
