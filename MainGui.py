import json
import dearpygui.dearpygui as dpg

from Chart import Charts
from Exchange import Exchange
from Settings import Settings


class MainGui():


    def __init__(self) -> None:
        # This is an Exchange object
        # self.ccxt = api

        # Primary window setup
        self.primary_window_width = 2000
        self.primary_window_height = int(self.primary_window_width * 0.5625) # 16:9 (9/16 ratio


        # Dearpygui setup
        dpg.create_context()
        dpg.configure_app(init_file="dpg.ini")

        # Launch program
        self.launch_program()


        dpg.create_viewport(title='Idk Yet', width=self.primary_window_width, height=self.primary_window_height, resizable=False)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)
        dpg.start_dearpygui()

        dpg.destroy_context()


    def launch_program(self):
        """ This is the primary window for all other windows and it shows a menu bar at the top which works as a nav bar for 
    other windows that are added on top of this one. 
        """
        with dpg.window(label="Main Menu", tag="main", no_resize=True, no_scrollbar=True):
            self.start = Settings()


# ftx = Exchange("ftx")
gui = MainGui()