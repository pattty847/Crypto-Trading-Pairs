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
                    charts = Charts(self.settings, self.exchange)
                    charts.launch_settings_panel()

        except FileNotFoundError as e:
            # If not create one with default data. 
            month_ago = self.do.get_time_in_past(minutes=0, days=30) # This will get the timestamp from a month ago
            setting_init = {"exchange":{"name":"", "key":"", "secret":""}, "last_symbol": "BTC/USDT", "last_timeframe": "1h", "last_since": month_ago, "favorite_symbols": ["BTC/USDT", "ETH/USDT", "LINK/USDT", "SOL/USDT"]}
            self.settings = setting_init
            with open("settings.json", "w") as jsonFile:
                json.dumps(setting_init)