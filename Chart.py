from utils.DoStuff import DoStuff

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json

class Charts():

    def __init__(self, settings, ccxt) -> None:
        self.settings = settings
        self.api = ccxt
        self.do = DoStuff()

        self.chart_id = 0

    def launch_trade_panel(self, main):
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
                    dpg.add_button(label='Cancel', height=48, width=-1)


    def add_chart(self):
        candles = self.api.get_candles(self.settings['last_symbol'], self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        self.chart_id += 1
        print(self.chart_id)

        with dpg.tab(label=f"{self.settings['last_symbol']}", parent="charts-tab", tag=f"chart-tab-{self.chart_id}"):
            # with dpg.collapsing_header(label="Sym/TF"):
            #     with dpg.group(horizontal=True):
            #         with dpg.group(horizontal=False, width=250):
            #             dpg.add_input_text(tag=f"symbols-searcher-{self.chart_id}", hint="Search",
            #                                callback=lambda sender, data: self.searcher(f"symbols-searcher-{self.chart_id}", 
            #                                f"symbol-{self.chart_id}", self.api.symbols))
            #             dpg.add_listbox(self.api.symbols, tag=f'symbol-{self.chart_id}', show=True, callback=lambda a, s: self.change_symbol(a, s, self.chart_id))
                    
            #         dpg.add_listbox(self.api.timeframes, callback=lambda a, s : self.change_timeframe(a, s, self.chart_id), width=100)
            with dpg.group(horizontal=True):
                symbol = dpg.add_selectable(label="Symbol", width=50)
                timeframe = dpg.add_selectable(label="TF", width=15)
                with dpg.popup(symbol, mousebutton=dpg.mvMouseButton_Left):
                    dpg.add_input_text(tag=f"symbols-searcher-{self.chart_id}", hint="Search",
                                            callback=lambda sender, data: self.searcher(f"symbols-searcher-{self.chart_id}", 
                                            f"symbol-{self.chart_id}", self.api.symbols))
                    dpg.add_listbox(self.api.symbols, tag=f'symbol-{self.chart_id}', show=True, callback=lambda a, s: self.change_symbol(a, s, self.chart_id))

                with dpg.popup(timeframe, mousebutton=dpg.mvMouseButton_Left):
                    dpg.add_listbox(self.api.timeframes, callback=lambda a, s : self.change_timeframe(a, s, self.chart_id), width=100)

            with dpg.subplots(2, 1, label="", width=-1, height=-1, link_all_x=True):
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
                        dpg.add_bar_series(dates, volume, tag=f'volume-series-{self.chart_id}')
                        dpg.fit_axis_data(dpg.top_container_stack())
                        dpg.fit_axis_data(xaxis_volume_tag)


    def launch_charts(self):
        """ This is the main candlestick and volume charts for the program, upon startup it will build the chart from the last saved ticker and timeframe. Then allow the user to select
        any symbol and timeframe they want. 
        """

        with dpg.child_window(label="Charts", tag="charts-window", parent="main"):
            with dpg.tab_bar(tag="charts-tab"):
                dpg.add_tab_button(label="+", trailing=True, callback=self.add_chart)

    def draw_menu(self):
        with dpg.menu_bar(tag='main-menu-bar', parent="main"):
            with dpg.menu(label="Menu"):
                dpg.add_menu_item(label="Charts", callback=self.launch_charts)
                dpg.add_menu_item(label="Trade", callback=self.launch_trade_panel)
                dpg.add_menu_item(label="Demo", callback=lambda:demo.show_demo())


            with dpg.menu(label="Date"):
                # date = datetime.today().strftime('%Y-%m-%d').split("-")
                date = self.settings['last_since'].split("T")[0].split("-")
                print(date)
                year = str(int(date[0][2:]))
                year_ = f'1{year}'
                dates = {'month_day': int(date[2]), 'year':int(year_), 'month':int(date[1])}
                print(dates)
                
                dpg.add_date_picker(level=dpg.mvDatePickerLevel_Day, label='From', default_value=dates)


    def change_symbol(self, s, app_data, u):
        candles = self.api.get_candles(app_data, self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        dpg.configure_item(f'candle-series-{u}', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
        dpg.configure_item(f"chart-tab-{u}", label=app_data)
        dpg.fit_axis_data(f'candle-series-yaxis-{u}')
        dpg.fit_axis_data(f'candle-series-xaxis-{u}')
        self.update_settings({"last_symbol":app_data})

    
    def change_timeframe(self, s, app_data, u):
        candles = self.api.get_candles(self.settings['last_symbol'], app_data, self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        dpg.configure_item(f'candle-series-{u}', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(app_data))
        # dpg.configure_item(f"chart-tab-{u}", label=app_data)
        dpg.fit_axis_data(f'candle-series-yaxis-{u}')
        dpg.fit_axis_data(f'candle-series-xaxis-{u}')
        self.update_settings({"last_timeframe":app_data})

    
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