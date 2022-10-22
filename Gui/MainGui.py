import dearpygui.dearpygui as dpg
import dearpygui.demo as demo

import Charts as charts


class MainGui():


    def __init__(self) -> None:

        # Primary window setup
        self.primary_window_width = 2000
        self.primary_window_height = int(self.primary_window_width * 0.5625) # 16:9 (9/16 ratio

        self.side_panel_width = 400


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


    def launch_program(self):
        with dpg.window(tag="Main", no_resize=True, no_scrollbar=True):
            with dpg.menu_bar(tag='menu-bar'):
                with dpg.menu(label="Menu"):

                    dpg.add_text("This menu is just for show!")
                    dpg.add_menu_item(label="New")
                    dpg.add_menu_item(label="Open")

                    with dpg.menu(label="Open Recent"):

                        dpg.add_menu_item(label="harrel.c")
            with dpg.window(label="Main Menu", tag="primary-window", no_resize=True, no_scrollbar=True, width=500, height=350):
                dpg.add_button(label="ImGui Demo", callback=lambda:dpg.show_imgui_demo())
                dpg.add_button(label="ImPlot Demo", callback=lambda:dpg.show_implot_demo())
                dpg.add_button(label="Demo", callback=lambda:demo.show_demo())
                dpg.add_button(label="Charts", callback=charts.launch_charts)
    


gui = MainGui()