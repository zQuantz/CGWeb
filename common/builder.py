from common.const import COLS, COLS_FMT, PARSER
from common.connector import Connector
from common.utils.html import html
from datetime import datetime
from bs4 import BeautifulSoup
from ticker import Ticker
import pandas as pd
import numpy as np

class Builder:

	def __init__(self):

		self.connector = Connector()

		self.tickers = {}

		self.initialize()
		self.generate_data_coords()
		self.generate_position_info_rows()

	def initialize():

		self.ticker_date_coords = self.connector.get_ticker_date_coords()
		self.ticker_info = self.connector.get_ticker_info()

	def fetch_ticker(self, ticker, date):

		if ticker in self.tickers:

			if date in self.tickers[ticker]: 
				return self.tickers[ticker][date]

		else:

			self.tickers[ticker] = {}

		option_chain = self.connector.get_data((ticker,),(date,), "options")
		ohlc = self.connector.get_data((ticker,),(date,), "ohlc")

		self.tickers[ticker][date] = Ticker(option_chain, ohlc)

	def generate_position_info_rows(self):

		N_ELEMENTS = 16

		def generate_row(elements, row_attributes):

			attributes = [{}]*N_ELEMENTS
			attributes[0] = {"style" : "width: 0.25rem;"}
			attributes[4] = {"style" : "width: 0.75rem;"}
			attributes[10] = {"style" : "width: 0.75rem;"}
			attributes[15] = {"style" : "width: 0.25rem;"}

			row = ""
			for element, attribute in zip(elements, attributes):
				row += html("td", element, attribute)
			return html("tr", row, row_attributes)

		attributes = [""]*N_ELEMENTS
		empty_option_row = generate_row(attributes, {"class" : "positionRow"})

		attributes[2] = "Aggregates"
		empty_agg_row = generate_row(attributes, {"class" : "positionTotalRow"})

		attributes = [
			"",
			html("a", "X", {"onclick" : 'removeFromPosition("OPTION_ID")', "href" : "#"}),
			"OPTION_ID",
			"QTY",
			"",
			"COST_PER_UNIT",
			"PREMIUM",
			"IV",
			"MONEYNESS",
			"PCT_PREMIUM",
			"",
			"DELTA_SHARES",
			"DELTA_$",
			"VEGA_$",
			"THETA_$",
			""
		]
		option_row = generate_row(attributes, {"class" : "positionRow"})

		attributes = [
			"",
			"",
			"Aggregates",
			"",
			"",
			"",
			"TOTAL_PREMIUM",
			"",
			"",
			"TOTAL_PCT_PREMIUM",
			"",
			"TOTAL_DELTA_SHARES",
			"TOTAL_DELTA_$",
			"TOTAL_VEGA_$",
			"TOTAL_THETA_$",
			""
		]
		agg_row = generate_row(attributes, {"class" : "positionTotalRow"})

		self.position_info = {
			"empty_option_row" : empty_option_row,
			"option_row" : option_row,
			"agg_row" : agg_row,
			"empty_agg_row" : empty_agg_row
		}

	def generate_data_coords(self):

		dates = set([
			item
			for sublist in self.ticker_date_coords.values()
			for item in sublist
		])
		dates = {
			date : (datetime.now() - datetime.strptime(date, "%Y-%m-%d")).days
			for date in dates
		}
		self.unique_dates = {
			date : html("option", date, {"data-subtext" : f"T-{dates[date]} Days"})
			for date in dates
		}

		self._option_tickers = ""
		for ticker in self.ticker_info:

			if ticker not in self.ticker_date_coords:
				continue

			self._option_tickers += html("option", ticker, {
				"data-subtext" : self.ticker_info[ticker]['full_name']
			})
