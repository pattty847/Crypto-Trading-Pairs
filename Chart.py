from tokenize import group
import dearpygui.dearpygui as dpg

class Charts():

    def __init__(self, settings) -> None:
        self.settings = settings

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


    def launch_charts(self, ccxt):

        width = 1100
        height = 800
        self.ccxt = ccxt

        with dpg.window(label="Charts", tag="charts-window", width=width, height=height, pos=[410, 25], no_resize=True):
            with dpg.menu_bar(tag='charts-menu-bar'):
                with dpg.menu(label="Menu"):
                    dpg.add_menu_item(label="Trade Panel", callback=self.launch_trade_panel)
                    with dpg.menu(label="Settings"):
                        self._add_config_options(
                            "charts-window", 3, 
                            "no_title_bar", "no_scrollbar", "menubar", 
                            "no_move", "no_resize", "no_collapse",
                            "no_close", "no_background", "no_bring_to_front_on_focus"
                        )

                    self.orderbook_matrix(ccxt.api.fetch_order_book("BTC/USDT"))

            with dpg.group(horizontal=True):
                with dpg.child_window(height=-1, width = width - (width*.27)):
                    series = self.orderbook_matrix(ccxt.api.fetch_order_book("BTC/USDT"))

                    with dpg.plot(label=f"Charts", tag='charts-plot', height=-1, width=-1):
                        dpg.add_plot_legend()
                        dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='candle-series-xaxis', time=True)
                        with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='candle-series-yaxis'):
                            dpg.add_candle_series([], [], [], [], [], tag='candle-series', time_unit=dpg.mvTimeUnit_Day)
                        with dpg.plot_axis(dpg.mvYAxis, label=""):
                            series = [float(float(i)/max(series)).__round__(4) for i in series]

                            dpg.add_heat_series(series, 100, 1,tag="series", scale_min=min(series), scale_max=max(series), format='')
                            dpg.fit_axis_data('candle-series-yaxis')
                            dpg.fit_axis_data('candle-series-xaxis')
                            print(dpg.get_item_configuration("series"))

                with dpg.child_window(height=-1, width=-1):
                    with dpg.group(horizontal=False):
                        dpg.add_button(label="Refresh", width=-1)
                        search = ["Item1", "Item2", "Item3"] # Temporary
                        dpg.add_input_text(tag="main_listbox_searcher", hint="Symbol", 
                                    callback=lambda sender, data: self.searcher("main_listbox_searcher", "main_listbox_result", search)) # TODO: Change the item list

                        dpg.add_listbox(search, tag="main_listbox_result", num_items=5)


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