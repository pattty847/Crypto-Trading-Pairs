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
        self.viewport_width = 1600
        self.viewport_height = 900
        self.side_panel_width = 300 # 2 buttons width = 75

        # TODO: Check if settings file is not created yet and if not make one with default settings.
        if not isfile("settings.json"):
            month_ago = self.do.get_time_in_past(0, 30)
            setting_init = {"last_ticker": "BTC/USDT", "last_timeframe": "1h", "last_since": month_ago}
            self.settings = setting_init
            with open("settings.json", "w") as settings_file:
                json.dump(setting_init, settings_file)
        else:
            with open("settings.json", "r") as jsonFile:
                self.settings = json.load(jsonFile)


    
    def run(self):
        with dpg.child_window(width=-1, height=-1):
            with dpg.menu_bar():
                dpg.add_menu(label="Menu Options")
            with dpg.child_window(autosize_x=True, autosize_y=True, pos=[self.viewport_width - self.side_panel_width, 10]):
                with dpg.collapsing_header(label="Trade"):
                    # with dpg.group(horizontal=True):
                    #     dpg.add_text("Text")
                    #     dpg.add_text("Text")
                    #     dpg.add_text("Text")
                    with dpg.group(horizontal=True):
                        with dpg.group(horizontal=False):
                            dpg.add_text("Symbol")
                            dpg.add_listbox(['1', '2', '3'], width=75)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Timeframe")
                            dpg.add_listbox(['1', '2', '3'], width=75)
                        with dpg.group(horizontal=False):
                            dpg.add_text("Period")
                            dpg.add_listbox(['1', '2', '3'], width=75)

                with dpg.collapsing_header(label="Indicators"):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Text")
                        dpg.add_text("Text")
                        dpg.add_text("Text")
                    with dpg.group(horizontal=True):
                        dpg.add_listbox(['1', '2', '3'], width=75)
                        dpg.add_listbox(['1', '2', '3'], width=75)
                        dpg.add_listbox(['1', '2', '3'], width=75)
                    
            # with dpg.child_window(autosize_x=True, height=175):
            #     with dpg.group(horizontal=True, width=0):
            #         with dpg.child_window(width=102, height=150):
            #             with dpg.tree_node(label="Nav 1"):
            #                 dpg.add_button(label="Button 1")
            #             with dpg.tree_node(label="Nav 2"):
            #                 dpg.add_button(label="Button 2")
            #             with dpg.tree_node(label="Nav 3"):
            #                 dpg.add_button(label="Button 3")
            #         with dpg.child_window(width=300, height=150):
            #             dpg.add_button(label="Button 1")
            #             dpg.add_button(label="Button 2")
            #             dpg.add_button(label="Button 3")
            #         with dpg.child_window(width=50, height=150):
            #             dpg.add_button(label="B1", width=25, height=25)
            #             dpg.add_button(label="B2", width=25, height=25)
            #             dpg.add_button(label="B3", width=25, height=25)
            # with dpg.group(horizontal=True):
            #     dpg.add_button(label="Footer 1", width=175)
            #     dpg.add_text("Footer 2")
            #     dpg.add_button(label="Footer 3", width=175)
            


    def set_up(self):
        # This is the first step to use the dearpygui library.
        dpg.create_context()

        with dpg.window(tag="Main", no_resize=True, no_scrollbar=True):
            self.run()
            # with dpg.menu_bar():
            #     with dpg.menu(label='Charts'):
            #         dpg.add_button(label="Open", callback=self.charts_window)

            #     with dpg.menu(label='Demo'):
            #         dpg.add_button(label="Open", callback=self.demo)

            #     with dpg.menu(label="Cointegration"):
            #         dpg.add_button(label="Open", callback=self.cointegration)

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


gui = Graphics("ftx")
gui.set_up()