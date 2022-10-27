from utils.DoStuff import DoStuff

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import json

class Charts():

    def __init__(self, settings, ccxt) -> None:
        self.settings = settings
        self.api = ccxt
        self.do = DoStuff()

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

            with dpg.group(horizontal=False):
                # step will need to equal exchange min order size
                dpg.add_input_float(label="Limit Price", tag='limit-price', min_value=0, max_value=1000000, width=115, step=0, step_fast=0, callback=lambda:print(dpg.get_value('limit-price')), format="%.04f")
                dpg.add_slider_int(label="Leverage", tag="leverage", min_value=1, max_value=100, callback=lambda:print(dpg.get_value("leverage")))
            
            with dpg.group(horizontal=True):
                dpg.add_button(tag='limit', label="Limit", width=400/2-30)
                # dpg.add_theme_color("limit", self._hsv_to_rgb(2/7.0, 0.6, 0.6))r
                dpg.add_button(label="Market", width=-1)

            with dpg.group(width=-1):
                dpg.add_button(label="Buy", height=20)
                dpg.add_button(label="Sell", height=20)



    def launch_charts(self):
        """ This is the main candlestick and volume charts for the program, upon startup it will build the chart from the last saved ticker and timeframe. Then allow the user to select
        any symbol and timeframe they want. 
        """
        candles = self.api.get_candles(self.settings['last_symbol'], self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)

        with dpg.child_window(label="Charts", tag="charts-window", width=-1, height=-1, parent="main"):

            with dpg.subplots(2, 1, label="", width=-1, height=-1, link_all_x=True) as subplot_id:
                with dpg.plot(label=f"Charts", tag='charts-plot'):
                    dpg.add_plot_legend()

                    dpg.add_plot_axis(dpg.mvXAxis, tag='candle-series-xaxis', time=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='candle-series-yaxis'):
                        dpg.add_candle_series(dates, opens, closes, lows, highs, tag='candle-series', time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
                        dpg.fit_axis_data(dpg.top_container_stack())
                        dpg.fit_axis_data('candle-series-xaxis')

                    with dpg.plot_axis(dpg.mvYAxis):
                        dpg.add_heat_series(dates, closes)

                        
                with dpg.plot(label=f"Volume", tag='volume-plot'):
                    dpg.add_plot_legend()
                    dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='volume-series-xaxis', time=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='volume-series-yaxis'):
                        dpg.add_bar_series(dates, volume)
                        dpg.fit_axis_data(dpg.top_container_stack())
                        dpg.fit_axis_data('volume-series-xaxis')

    def draw_menu(self):
        with dpg.menu_bar(tag='main-menu-bar', parent="main"):
            with dpg.menu(label="Menu"):
                dpg.add_menu_item(label="Charts", callback=self.launch_charts)
                dpg.add_menu_item(label="Trade", callback=self.launch_trade_panel)
                dpg.add_menu_item(label="Demo", callback=lambda:demo.show_demo())
                
            with dpg.menu(label="Symbols"):
                dpg.add_input_text(tag="symbols-searcher", hint="Search",
                                callback=lambda sender, data: self.searcher("symbols-searcher", "symbol", self.api.symbols))
                dpg.add_listbox(self.api.symbols, tag='symbol', show=True, callback=self.change_symbol)

            with dpg.menu(label="TF"):
                dpg.add_listbox(self.api.timeframes, callback=self.change_timeframe)


    def change_symbol(self, s, app_data, u):
        candles = self.api.get_candles(app_data, self.settings['last_timeframe'], self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(self.settings['last_timeframe']))
        dpg.fit_axis_data('candle-series-yaxis')
        dpg.fit_axis_data('candle-series-xaxis')
        self.update_settings({"last_symbol":app_data})

    
    def change_timeframe(self, s, app_data, u):
        candles = self.api.get_candles(self.settings['last_symbol'], app_data, self.settings['last_since'])
        dates, opens, closes, lows, highs, volume = self.do.candles_to_list(candles)
        dpg.configure_item('candle-series', dates=dates, opens=opens, closes=closes, highs=highs, lows=lows, time_unit=self.do.convert_timeframe(app_data))
        dpg.fit_axis_data('candle-series-yaxis')
        dpg.fit_axis_data('candle-series-xaxis')
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