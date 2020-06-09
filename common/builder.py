from common.connector import Connector
from common.utils.html import html
from common.ticker import Ticker
from datetime import datetime

class Builder:

	def __init__(self):

		self.connector = Connector()

		self.tickers = {}

		self.initialize()
		self.generate_data_coords()
		self.generate_position_info_rows()

	def initialize(self):

		print("Collecting Ticker Dates")
		self.ticker_dates = self.connector.get_ticker_dates()

		print("Collecting Ticker Info")
		self.ticker_info = self.connector.get_ticker_info()

	def fetch_ticker(self, ticker, date):

		if not ticker:

			self.ticker = None
			return

		if ticker in self.tickers:

			if date in self.tickers[ticker]:
				
				self.ticker = self.tickers[ticker][date]
				return

		else:

			self.tickers[ticker] = {}

		option_chain = self.connector.get_data((ticker,),(date,), "options")
		ohlc = self.connector.get_data((ticker,),(date,), "ohlc")
		key_stats = self.connector.get_data((ticker,),(date,), "key_stats")

		self.ticker = Ticker(ticker, date, option_chain, ohlc, key_stats, self.ticker_info[ticker])
		self.tickers[ticker][date] = self.ticker

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
			for sublist in self.ticker_dates.values()
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

			if ticker not in self.ticker_dates:
				continue

			self._option_tickers += html("option", ticker, {
				"data-subtext" : self.ticker_info[ticker]['full_name']
			})
