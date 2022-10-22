import dearpygui.dearpygui as dpg


def launch_trade_panel():
    with dpg.window():
        pass


def launch_charts():

    width = 800
    height = 800

    with dpg.window(label="Charts", tag="charts-window", width=width, height=height):
        dpg.add_button(label="Trade Panel", callback=launch_trade_panel)
        with dpg.plot(label=f"Charts", tag='chart-title', height=-1, width=-1):
            dpg.add_plot_legend()
            dpg.add_plot_axis(dpg.mvXAxis, label="Date", tag='candle-series-xaxis', time=True)
            with dpg.plot_axis(dpg.mvYAxis, label="USD", tag='candle-series-yaxis'):
                dpg.add_candle_series([], [], [], [], [], tag='candle-series', time_unit=dpg.mvTimeUnit_Day)
                dpg.fit_axis_data(dpg.top_container_stack())