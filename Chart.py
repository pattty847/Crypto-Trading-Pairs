from utils.DoStuff import DoStuff
from utils.CoinalyzeStats import Stats

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json

class Charts():

    def __init__(self, settings, ccxt) -> None:
        self.settings = settings
        self.api = ccxt
        self.do = DoStuff()

        self.chart_id = 0

    def launch_trade_panel(self):
        with dpg.window(label="Trade", tag="trade-window", width=400, height=500, pos=[0, 25]):

            with dpg.menu_bar(tag='trade-menu-bar'):

                with dpg.menu(label="Menu"):

                    with dpg.menu(label="Settings"):

                        self._add_config_options(
                            "trade-window", 3, 
                            "no_title_bar", "no_scrollbar", "menubar", 
                            "no_move", "no_resize", "no_collapse",
                            "no_close", "no_background", "no_bring_to_front_on_focus"
                        )
            with dpg.group():

                dpg.add_input_float(label="Limit", default_value=20000, format="%.06f", width=-1)

            with dpg.table(header_row=False, borders_innerH=True, 
                    borders_outerH=True, borders_innerV=True, 
                    borders_outerV=True, width=-1):
            
                # Add two columns
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

                    dpg.add_button(label='Cancel', height=48, width=-1)\


    def launch_stats_panel(self):

        with dpg.window(label="Crypto Stats", tag="stats-window", width=-1, height=-1, pos=[0, 25]):
           
            s = Stats()
            
            with dpg.table(label='DatasetTable') as stats_window:
                
                for i in range(s.stats.shape[1]):                    # Generates the correct amount of columns
                    dpg.add_table_column(label=s.stats.columns[i])   # Adds the headers
                
                for i in range(s.stats.shape[0]):                    # Shows the first n rows
                    
                    with dpg.table_row():
                        
                        for j in range(s.stats.shape[1]):
                            
                            dpg.add_text(f"{s.stats.iloc[i,j]}")
            
            self._add_config_options(stats_window, 1, 
                "borders_innerV", "borders_outerV", "resizable", before=stats_window)


    def launch_indicator_panel(self):
        
        with dpg.window(label="Indicator", tag="indicator-window", width=400, height=500, pos=[0, 25]):

            indicator_list = ["RSI", "MACD", "MFI", "SMA", "EMA"]
            with dpg.table(header_row=False):

                for col in range(4):
                    dpg.add_table_column()

                for item in indicator_list:
                    with dpg.table_row():
                        dpg.add_selectable(label=item)
                


    def add_chart(self):

        candles = self.api.get_candles(self.settings['last_symbol'], self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        self.chart_id += 1

        with dpg.tab(label=f"{self.settings['last_symbol']}", parent="charts-tab", tag=f"chart-tab-{self.chart_id}"):

            with dpg.group(horizontal=True):

                symbol = dpg.add_selectable(label="Symbol", width=50)
                timeframe = dpg.add_selectable(label="TF", width=15)
                date = dpg.add_selectable(label="Date", width=30)
                dpg.add_selectable(label="Indicator", callback=self.launch_indicator_panel, width=62)

                with dpg.popup(symbol, mousebutton=dpg.mvMouseButton_Left):

                    dpg.add_input_text(tag=f"symbols-searcher-{self.chart_id}", hint="Search",
                                            callback=lambda sender, data: self.searcher(f"symbols-searcher-{self.chart_id}", 
                                            f"symbol-{self.chart_id}", self.api.symbols))

                    dpg.add_listbox(self.api.symbols, tag=f'symbol-{self.chart_id}', show=True, callback=lambda s, a: self.change_symbol(s, a, self.chart_id))

                with dpg.popup(timeframe, mousebutton=dpg.mvMouseButton_Left):

                    dpg.add_listbox(self.api.timeframes, tag=f'timeframe-{self.chart_id}', callback=lambda s, a : self.change_timeframe(s, a, self.chart_id), width=100)

                with dpg.popup(date, mousebutton=dpg.mvMouseButton_Left):
                    # The default date will be the last saved date in the settings file

                    date = self.settings['last_since'].split("T")[0].split("-")
                    year = str(int(date[0][2:]))
                    year_ = f'1{year}'
                    since = {'month_day': int(date[2]), 'year':int(year_), 'month':int(date[1])}
                    
                    dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day, label='From', default_value=since)

            with dpg.subplots(2, 1, label="", width=-1, height=-1, link_all_x=True, row_ratios=[1.0, 0.25]):

                with dpg.plot():

                    dpg.add_plot_legend()
                    xaxis_candle_tag = f'candle-series-xaxis-{self.chart_id}'
                    dpg.add_plot_axis(dpg.mvXAxis, tag=xaxis_candle_tag, time=True)

                    with dpg.plot_axis(dpg.mvYAxis, tag=f'candle-series-yaxis-{self.chart_id}', label="USD"):

                        dpg.add_candle_series(dates, opens, closes, lows, highs, tag=f'candle-series-{self.chart_id}', time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
                        dpg.fit_axis_data(dpg.top_container_stack())
                        dpg.fit_axis_data(xaxis_candle_tag)
                        
                with dpg.plot():

                    dpg.add_plot_legend()
                    xaxis_volume_tag = f'volume-series-xaxis-{self.chart_id}'
                    dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag=xaxis_volume_tag, time=True)

                    with dpg.plot_axis(dpg.mvYAxis, label="USD", tag=f'volume-series-yaxis-{self.chart_id}'):

                        dpg.add_bar_series(dates, volume, tag=f'volume-series-{self.chart_id}', weight=1)
                        dpg.fit_axis_data(dpg.top_container_stack())
                        dpg.fit_axis_data(xaxis_volume_tag)


    def launch_charts(self):
        """This is the main child window that is attached to the primary window. It contains the tab bar which other tabs are attached to via tag.
        """

        with dpg.child_window(label="Charts", tag="charts-window", parent="main"):

            with dpg.tab_bar(tag="charts-tab"):

                dpg.add_tab_button(label="+", trailing=True, callback=self.add_chart)
                with dpg.tooltip(parent=dpg.last_item()):
                    dpg.add_text("Click to add charts.")

    def draw_menu(self):

        with dpg.menu_bar(tag='main-menu-bar', parent="main"):

            with dpg.group(horizontal=True):
                dpg.add_menu_item(label="Trade", callback=self.launch_trade_panel)
                dpg.add_menu_item(label="Stats", callback=self.launch_stats_panel)
                
            
            with dpg.menu(label="DPG"):
                dpg.add_menu_item(label="Debug", callback=dpg.show_debug)
                dpg.add_menu_item(label="ImGui", callback=dpg.show_imgui_demo)
                dpg.add_menu_item(label="ImPlot", callback=dpg.show_implot_demo)
                dpg.add_menu_item(label="Demo", callback=demo.show_demo)

            with dpg.menu(label="Save"):
                dpg.add_menu_item(label="Save Window Configurations", callback=lambda: self.save_init())


    def change_symbol(self, sender, app_data, user_data):
        print(sender[-1], app_data, user_data)

        chart_id = sender[-1]

        candles = self.api.get_candles(app_data, self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)

        dpg.configure_item(f'candle-series-{chart_id}', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
        dpg.configure_item(f"chart-tab-{chart_id}", label=app_data)

        dpg.fit_axis_data(f'candle-series-yaxis-{chart_id}')
        dpg.fit_axis_data(f'candle-series-xaxis-{chart_id}')

        dpg.configure_item(f"volume-series-{chart_id}", x=dates, y=volume)
        dpg.fit_axis_data(f'volume-series-yaxis-{chart_id}')
        dpg.fit_axis_data(f'volume-series-xaxis-{chart_id}')

        self.update_settings({"last_symbol":app_data})

    
    def change_timeframe(self, sender, app_data, user_data):
        print(sender[-1], app_data, user_data)
        chart_id = sender[-1]
        

        candles = self.api.get_candles(self.settings['last_symbol'], app_data, self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)

        dpg.configure_item(f'candle-series-{chart_id}', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(app_data))
        dpg.fit_axis_data(f'candle-series-yaxis-{chart_id}')
        dpg.fit_axis_data(f'candle-series-xaxis-{chart_id}')
        
        dpg.configure_item(f"volume-series-{chart_id}", x=dates, y=volume)
        dpg.fit_axis_data(f'volume-series-yaxis-{chart_id}')
        dpg.fit_axis_data(f'volume-series-xaxis-{chart_id}')

        self.update_settings({"last_timeframe":app_data})


    def _add_config_options(self, item, columns, *names, **kwargs):
        
        if columns == 1:
            if 'before' in kwargs:
                for name in names:
                    dpg.add_checkbox(label=name, callback=self._config, user_data=item, before=kwargs['before'], default_value=dpg.get_item_configuration(item)[name])
            else:
                for name in names:
                    dpg.add_checkbox(label=name, callback=self._config, user_data=item, default_value=dpg.get_item_configuration(item)[name])

        else:

            if 'before' in kwargs:
                dpg.push_container_stack(dpg.add_table(header_row=False, before=kwargs['before']))
            else:
                dpg.push_container_stack(dpg.add_table(header_row=False))

            for i in range(columns):
                dpg.add_table_column()

            for i in range(int(len(names)/columns)):

                with dpg.table_row():
                    for j in range(columns):
                        dpg.add_checkbox(label=names[i*columns + j], 
                                            callback=self._config, user_data=item, 
                                            default_value=dpg.get_item_configuration(item)[names[i*columns + j]])
            dpg.pop_container_stack()


    def _config(self, sender, keyword, user_data):

        widget_type = dpg.get_item_type(sender)
        items = user_data

        if widget_type == "mvAppItemType::mvRadioButton":
            value = True

        else:
            keyword = dpg.get_item_label(sender)
            value = dpg.get_value(sender)

        if isinstance(user_data, list):
            for item in items:
                dpg.configure_item(item, **{keyword: value})
        else:
            dpg.configure_item(items, **{keyword: value})


    def update_settings(self, x):

        self.settings.update(x)
        with open("settings.json", "w") as jsonFile:
            json.dump(self.settings, jsonFile)


    def orderbook_matrix(self, orderbook):

        from pprint import pprint
        matrix = []
        bids = orderbook['bids']
        asks = orderbook['asks'][::-1] # This will sort in descending order
        best_bid = bids[-1]
        best_ask = asks[0]

        for i in range(len(asks)):
            matrix.append(asks[i][1])
        for i in range(len(bids)):
            matrix.append(bids[i][1])

        return matrix

    
    def _add_config_options(self, item, columns, *names, **kwargs):
    
        if columns == 1:
            if 'before' in kwargs:
                for name in names:
                    dpg.add_checkbox(label=name, callback=self._config, user_data=item, before=kwargs['before'], default_value=dpg.get_item_configuration(item)[name])
            else:
                for name in names:
                    dpg.add_checkbox(label=name, callback=self._config, user_data=item, default_value=dpg.get_item_configuration(item)[name])

        else:

            if 'before' in kwargs:
                dpg.push_container_stack(dpg.add_table(header_row=False, before=kwargs['before']))
            else:
                dpg.push_container_stack(dpg.add_table(header_row=False))

            for i in range(columns):
                dpg.add_table_column()

            for i in range(int(len(names)/columns)):

                with dpg.table_row():
                    for j in range(columns):
                        dpg.add_checkbox(label=names[i*columns + j], 
                                            callback=self._config, user_data=item, 
                                            default_value=dpg.get_item_configuration(item)[names[i*columns + j]])
            dpg.pop_container_stack()


    def searcher(self, searcher, result, search_list):

        modified_list = []

        if dpg.get_value(searcher) == "*":
            modified_list.extend(iter(search_list))

        if dpg.get_value(searcher).lower():
            modified_list.extend(item for item in search_list if dpg.get_value(searcher).lower() in item.lower())

        dpg.configure_item(result, items=modified_list)


    def _config(self, sender, keyword, user_data):

        widget_type = dpg.get_item_type(sender)
        items = user_data

        if widget_type == "mvAppItemType::mvRadioButton":
            value = True

        else:
            keyword = dpg.get_item_label(sender)
            value = dpg.get_value(sender)

        if isinstance(user_data, list):
            for item in items:
                dpg.configure_item(item, **{keyword: value})
        else:
            dpg.configure_item(items, **{keyword: value})


    def save_init(self):

        dpg.save_init_file("dpg.ini")
        print("Saved window config.")