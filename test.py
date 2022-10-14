import dearpygui.dearpygui as dpg
from math import sin

dpg.create_context()


sindatax = []
sindatay = []
for i in range(0, 100):
    sindatax.append(i / 100)
    sindatay.append(0.5 + 0.5 * sin(50 * i / 100))

with dpg.window(label="Tutorial", width=400, height=400):
    with dpg.plot(label="Annotations", height=-1, width=-1):
        dpg.add_plot_legend()
        dpg.add_plot_axis(dpg.mvXAxis, label="x")
        dpg.add_plot_axis(dpg.mvYAxis, label="y")
        dpg.add_line_series(sindatax, sindatay, label="0.5 + 0.5 * sin(x)", parent=dpg.last_item())

        # annotations belong to the plot NOT axis
        dpg.add_plot_annotation(label="BL", default_value=(0.25, 0.25), offset=(-15, 15), color=[255, 255, 0, 255])
        dpg.add_plot_annotation(label="BR", default_value=(0.75, 0.25), offset=(15, 15), color=[255, 255, 0, 255])
        dpg.add_plot_annotation(label="TR not clampled", default_value=(0.75, 0.75), offset=(-15, -15),
                                color=[255, 255, 0, 255], clamped=False)
        dpg.add_plot_annotation(label="TL", default_value=(0.25, 0.75), offset=(-15, -15), color=[255, 255, 0, 255])
        dpg.add_plot_annotation(label="Center", default_value=(0.5, 0.5), color=[255, 255, 0, 255])

dpg.create_viewport(title='Custom Title', width=800, height=600)
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()