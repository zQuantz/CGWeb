import pandas as pd
import numpy as np
import sys, os

class IV:

	def __init__(self, connector):

		self.reset()
		self.connector = connector

	def reset(self):

		self.data = None
		self.symbol = None
		self.ticker = None

	def get_iv(self, ticker):

		if not ticker:
			self.reset()
			return

		self.ticker = ticker
		self.symbol = self.connector.ticker_info[ticker]['exchange_code']
		self.symbol += f":{ticker}"
		self.symbol = {
			"ticker" : ticker,
			"symbol" : self.symbol
		}

		time_iv = self.connector.get_time_iv(ticker)
		time_iv['date_current'] = pd.to_datetime(time_iv.date_current).astype(int) / (10 ** 6)
		
		time_iv['log_dte'] = time_iv.log_dte.astype(int).astype(str)
		time_iv = time_iv[['date_current', 'log_dte', 'IV']]

		time_iv = time_iv.pivot(index="date_current", columns="log_dte", values="IV") * 100
		time_iv = time_iv.ffill()

		data = time_iv.to_dict("list")
		data['dates'] = list(time_iv.index.astype(int))

		iv = self.connector.get_iv(ticker)
		data['Global'] = list(iv.IV.ffill() * 100)

		self.data = data
