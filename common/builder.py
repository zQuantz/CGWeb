from common.const import CONFIG, TAS_COLS, PT_COLS
from common.live_ticker import LiveTicker
from common.connector import Connector
from common.utils.html import html
from common.ticker import Ticker

from datetime import datetime
from hashlib import md5
import pandas as pd
import numpy as np

class Builder:

	def __init__(self):

		self.connector = Connector()

		self.tickers = {}

		self.initialize()
		self.generate_data_coords()
		self.generate_position_info_rows()
		self.generate_position_summary_rows()

	def initialize(self):

		print("Collecting Ticker Dates")
		self.ticker_dates = self.connector.get_ticker_dates()

		print("Collecting Ticker Info")
		self.ticker_info = self.connector.get_ticker_info()

		print("Collecting Interest Rates")
		self.rates = self.connector.get_rates()

		print("Collecting Table Lengths")
		self.lengths = self.connector.get_table_lengths()

	def update(self):

		updated = False
		lengths = self.connector.get_table_lengths()
		
		if lengths['options'] != self.lengths['options']:
		
			ticker_dates = self.connector.get_ticker_dates(isUpdate=True)		
			for ticker in ticker_dates:

				if ticker not in self.ticker_dates:
					self.ticker_dates[ticker] = ticker_dates[ticker]
				elif ticker_dates[ticker][0] not in self.ticker_dates[ticker]:
					self.ticker_dates[ticker] = ticker_dates[ticker] + self.ticker_dates[ticker]

			self.lengths['options'] = lengths['options']
			updated = True

		if lengths['instruments'] != self.lengths['instruments']:

			self.ticker_info = self.connector.get_ticker_info()
			self.lengths['instruments'] = lengths['instruments']
			updated = True

		if lengths['rates'] != self.lengths['rates']:

			self.rates = self.connector.get_rates()
			self.lengths['rates'] = lengths['rate']
			updates = True

		if updated: self.generate_data_coords()

		return updated

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

		if date == "LIVE":

			data = LiveTicker(ticker, self.rates)
			self.ticker = Ticker(ticker,
								 date,
								 data.options,
								 data.ohlc,
								 data.key_stats,
								 self.ticker_info[ticker])

		else:

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
			"QUANTITY",
			"",
			"COST_PER_UNIT",
			"PREMIUM",
			"I.V.",
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

	def generate_position_summary_rows(self):

		total_th = html("th", "Total Premium", {"scope" : "row", "colspan" : "4"})

		tds = ""
		tds += total_th
		tds += html("td", "", {})
		empty_agg_row = html("tr", tds, {})

		tds = ""
		tds += total_th
		tds += html("td", "TOTAL_PREMIUM", {})
		agg_row = html("tr", tds, {})

		tds = ""
		tds += html("th", "NUM", {"scope" : "row"})
		tds += html("td", "OPTION_ID", {})
		tds += html("td", "QUANTITY", {})
		tds += html("td", "PREMIUM", {})
		tds += html("td", "NET_PREMIUM", {})
		summary_row = html("tr", tds, {})

		self.position_summary = {
			"agg_row" : agg_row,
			"empty_agg_row" : empty_agg_row,
			"summary_row" : summary_row
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
		self.unique_dates['LIVE'] = html("option", "LIVE", {"data-subtext" : f"T-0 Seconds"})

		self._ticker_options = ""
		for ticker in self.ticker_info:

			if ticker not in self.ticker_dates:
				continue

			self._ticker_options += html("option", ticker, {
					"data-subtext" : self.ticker_info[ticker]['full_name']
				})

	def execute(self, data):

		password = CONFIG['salt'].format(PASSWORD=data['password'])
		password = md5(password.encode()).hexdigest()

		if password != self.connector.get_password(data['username']):
			return {
				"event" : "bad_password",
				"message" : f"Wrong password for user {data['username']}. Try Again."
			}

		###############################################################################################

		options = data['options']
		keys = list(options.keys())
		qtys = [options[key]['quantity'] for key in keys]

		idc = np.argsort(keys)
		position_id = f"{keys[idc[0]]},{qtys[idc[0]]}"
		for idx in idc[1:]:
			position_id += f",{keys[idx]},{qtys[idx]}"
		position_id = md5(position_id.encode()).hexdigest()

		###############################################################################################

		items = [
			[
				data['username'],
				datetime.now(),
				self.ticker.ticker,
				position_id,
				key,
				qty,
				options[key]['option']['option_type'],
				options[key]['option']['bid'],
				options[key]['option']['option_price'],
				options[key]['option']['ask'],
				options[key]['option']['delta'],
				options[key]['option']['gamma'],
				options[key]['option']['theta'],
				options[key]['option']['vega'],
				options[key]['option']['rho'],
				options[key]['option']['volume'],
				options[key]['option']['open_interest'],
				options[key]['option']['implied_volatility'],
				options[key]['option']['strike_price'],
				options[key]['option']['expiration_date'],
				options[key]['option']['time_to_expiry'],
				self.ticker.stock_price
			]
			for key, qty in zip(keys, qtys)
		]

		df = pd.DataFrame(items, columns = TAS_COLS)
		self.connector.write("timeandsales", df)

		###############################################################################################

		items = [
			items[0][:4] + [
				data['direction'],
				data['strategy'],
				data['sentiment'],
				data['notes'],
				data['filenames'],
				data['images']
			]
		]
		df = pd.DataFrame(items, columns = PT_COLS)
		self.connector.write("position_tags", df)

		###############################################################################################

		return {
			"event" : "success",
			"message" : "Position Added!"
		}