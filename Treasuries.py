import requests
import pandas as pd

class Treasuries():
    def __init__(self):
        self.base_url = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        self.endpoints = {
            "avg_interest_rates":"/v2/accounting/od/avg_interest_rates", 
            "debt_to_penny":"/v2/accounting/od/debt_to_penny"
        }

    def avg_interest_rates(self):
        fields = "record_date,security_type_desc,security_desc,avg_interest_rate_amt,record_fiscal_year"
        filter_by = 'record_fiscal_year:eq:2022,security_type_desc:in:Marketable'

        avg_interest_rates_ = f"{self.base_url}{self.endpoints['avg_interest_rates']}?fields={fields}&filter={filter_by}"
        resp = requests.get(avg_interest_rates_).json()
        df = pd.DataFrame(resp['data'])
        print(df)
        return df

    def debt_to_penny(self):
        fields = "record_date,tot_pub_debt_out_amt"
        filter_by = ''

        debt_to_penny_ = f"{self.base_url}{self.endpoints['debt_to_penny']}?fields={fields}&filter={filter_by}"
        resp = requests.get(debt_to_penny_).json()
        df = pd.DataFrame(resp['data'])
        return df

t = Treasuries()
print(t.debt_to_penny())