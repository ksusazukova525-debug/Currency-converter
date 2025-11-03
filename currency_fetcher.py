import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Dict, Optional


class CurrencyFetcher:

    def __init__(self):
        self.url = "https://cbr.ru/currency_base/daily/"
        self.rates = {}
        self.df = None

    def fetch_rates(self) -> bool:
        try:
            response = requests.get(self.url, timeout=10)
            response.raise_for_status()
            response.encoding = 'utf-8'
            soup = BeautifulSoup(response.text, 'html.parser')
            table = soup.find('table', {'class': 'data'})
            if not table:
                return False
            rows = table.find_all('tr')[1:]
            codes = []
            units = []
            names = []
            rates = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 5:
                    code = cols[1].text.strip()
                    unit = cols[2].text.strip()
                    name = cols[3].text.strip()
                    rate = cols[4].text.strip()
                    codes.append(code)
                    units.append(int(unit))
                    names.append(name)
                    rates.append(float(rate.replace(',', '.')))
            self.df = pd.DataFrame({
                'Код': codes,
                'Единиц': units,
                'Название': names,
                'Курс': rates
            })
            self.rates = {
                row['Код']: (row['Единиц'], row['Курс'])
                for _, row in self.df.iterrows()
            }
            self.rates['RUB'] = (1, 1.0)
            return True
        except requests.RequestException as e:
            print(f"Ошибка при загрузке данных: {e}")
            return False
        except Exception as e:
            print(f"Неожиданная ошибка: {e}")
            return False

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[float]:
        try:
            if from_currency not in self.rates or to_currency not in self.rates:
                return None
            from_units, from_rate = self.rates[from_currency]
            to_units, to_rate = self.rates[to_currency]
            amount_in_rub = amount * (from_rate / from_units)
            result = amount_in_rub * (to_units / to_rate)
            return round(result, 2)
        except Exception as e:
            print(f"Ошибка конвертации: {e}")
            return None

    def get_all_currencies(self) -> Dict[str, str]:
        if self.df is None:
            return {'RUB': 'Российский рубль'}
        currencies = dict(zip(self.df['Код'], self.df['Название']))
        currencies['RUB'] = 'Российский рубль'
        return currencies

    def get_currency_info(self, code: str) -> Optional[str]:
        if code not in self.rates:
            return None
        if code == 'RUB':
            return "Российский рубль (базовая валюта)"
        units, rate = self.rates[code]
        name = self.df[self.df['Код'] == code]['Название'].values[0]
        return f"{name}: {rate:.4f} руб. за {units} {code}"
