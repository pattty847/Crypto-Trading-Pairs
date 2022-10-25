import json
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

from genericpath import isfile
from Chart import Charts
from Exchange import Exchange


class MainGui():


    def __init__(self, api) -> None:
        self.ccxt = api

        # Primary window setup
        self.primary_window_width = 2000
        self.primary_window_height = int(self.primary_window_width * 0.5625) # 16:9 (9/16 ratio

        # Width for main menu 
        self.menu_width = 400
        self.menu_height = 350

        # Checks if the settings file is there if not makes it and sets default settings
        if not isfile("settings.json"):
            month_ago = self.do.get_time_in_past(0, 30)
            setting_init = {"last_symbol": "BTC/USDT", "last_timeframe": "1h", "last_since": month_ago, "favorite_symbols": ["BTC/USDT", "ETH/USDT", "LINK/USDT", "SOL/USDT"]}
            self.settings = setting_init
            with open("settings.json", "w") as settings_file:
                json.dump(setting_init, settings_file)
        else:
            # If we have a settings file open it
            with open("settings.json", "r") as jsonFile:
                self.settings = json.load(jsonFile)


        # Dearpygui setup
        dpg.create_context()

        # Launch program
        self.launch_program()


        dpg.create_viewport(title='Idk Yet', width=self.primary_window_width, height=self.primary_window_height, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("Main", True)
        dpg.start_dearpygui()

        dpg.destroy_context()


    # This is the primary window for all other windows and it shows a menu bar at the top which works as a nav bar for 
    # other windows that are added on top of this one. 
    def launch_program(self):
        with dpg.window(tag="Main", no_resize=True, no_scrollbar=True):
            with dpg.menu_bar(tag='main-menu-bar'):
                with dpg.menu(label="Menu"):
                    dpg.add_menu_item(label="Main Menu", callback=self.launch_main_menu)
                    

    # This is the main window which will be for the trading aspect of the program, now its used to launch demos. 
    def launch_main_menu(self):
        with dpg.window(label="Main Menu", tag="primary-window", no_resize=True, no_scrollbar=True, width=self.menu_width, height=self.menu_height, pos=[5, 25]):
            with dpg.group(horizontal=False, width=-1):
                dpg.add_button(label="ImGui Demo", callback=lambda:dpg.show_imgui_demo())
                dpg.add_button(label="ImPlot Demo", callback=lambda:dpg.show_implot_demo())
                dpg.add_button(label="Demo", callback=lambda:demo.show_demo())
                dpg.add_button(label="Charts", callback=self.launch_charts)
    
    
    # Callback that launches the charts window
    def launch_charts(self, a, s, u):
        self._log("Charts launching...", s, u)
        self.charts = Charts(self.settings)
        self.charts.launch_charts(self.ccxt)


    def _log(self, sender, app_data, user_data):
        print(f"sender: {sender}, \t app_data: {app_data}, \t user_data: {user_data}")


ftx = Exchange("ftx")
gui = MainGui(ftx)