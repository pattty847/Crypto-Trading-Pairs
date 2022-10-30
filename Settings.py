import json
import dearpygui.dearpygui as dpg

from Chart import Charts
from Exchange import Exchange

class Settings:

    def __init__(self) -> None:
        try:
            # If we have a settings file load it
            with open("settings.json", "r") as jsonFile:
                self.settings = json.load(jsonFile)
                if self.settings["exchange"]["name"] != "":
                    self.exchange = Exchange(self.settings['exchange']['name'])

                    charts = Charts(self.settings, self.exchange)
                    charts.draw_menu()
                    charts.launch_charts()
                else:
                    self.launch_settings_panel()
        except FileNotFoundError as e:
            # If not create one with default data. 
            month_ago = self.do.get_time_in_past(minutes=0, days=30) # This will get the timestamp from a month ago
            setting_init = {"exchange":{"name":"", "key":"", "secret":""}, "last_symbol": "BTC/USDT", "last_timeframe": "1h", "last_since": month_ago, "favorite_symbols": ["BTC/USDT", "ETH/USDT", "LINK/USDT", "SOL/USDT"]}
            self.settings = setting_init
            with open("settings.json", "w") as jsonFile:
                json.dumps(setting_init)

    def launch_settings_panel(self):
        with dpg.window(label="Connect Exchange", tag="settings-window", width=500, height=350, pos=[0, 25]):
            dpg.add_text("Exchange Settings")
            dpg.add_combo(['binance', 'ftx', 'coinbasepro', 'gateio', 'binanceus'], label="Exchange", tag='exchange')
            dpg.add_input_text(label="API KEY", multiline=False, height=300, tab_input=True, tag='key')
            dpg.add_input_text(label="API SECRET", multiline=False, height=300, tab_input=True, tag='secret')
            dpg.add_button(label="Connect", callback=self.connect_exchange)

    def connect_exchange(self):
        
        exchange_name = dpg.get_value('exchange')
        key = dpg.get_value('key')
        secret = dpg.get_value('secret')

        self.exchange = Exchange(exchange_name)

        self.settings.update({"exchange":{"name":exchange_name, "key":key, "secret":secret}})
        with open ("settings.json", "w") as jsonFile:
            json.dump(self.settings, jsonFile)


        charts = Charts(self.settings, self.exchange)
        charts.draw_menu()
        charts.launch_charts()