from common.utils.html import html
import pandas as pd
import numpy as np
import sys, os

class IV:

	def __init__(self, connector):

		self.reset()
		self.connector = connector
		self.html = {
			"iv_selector_table" : self.generate_iv_selector()
		}

	def generate_iv_selector(self):

		def td(label, _id):
		    e = html("button", label, {
		    	"class": "ivSelectButton",
		    	"id" : _id
		    })
		    return html("td", e)

		trs = []
		for maturity in [1, 2, 3, 6, 9, 12, 18, 24]:
		    
		    tr = td(f"{maturity}M {80}%", f"m{maturity}m{80}")
		    for moneyness in range(85, 125, 5):
		        
		        label = f"{maturity}M {moneyness}%"
		        tr += td(label, f"m{maturity}m{moneyness}")
		        
		    trs.append(html("tr", tr))

		tbody = html("tbody", "".join(trs))
		return html("table", tbody, {
			"id" : "ivSelectorTable",
			"class" : "table table-sm table-bordered"
		})

	def reset(self):

		self.data = None
		self.symbol = None
		self.ticker = None

	def get_surface(self, ticker):

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

		self.surface = self.connector.get_surface(ticker)
		self.surface['date_current'] = self.surface.date_current.astype(str)
		self.surface = self.surface.to_dict("list")
