from datetime import datetime, timedelta
from common.utils.html import html
import sqlalchemy as sql
import pandas as pd
import numpy as np
import sys, os
import json

from common.const import CONFIG

###################################################################################################

class Connector():

	HOUR_OFFSET = 22
	engine = sql.create_engine(CONFIG['db_address'])
	max_tries = 3
	moneyness = 0.1

	def __init__(self):

		print("Collecting Ticker Dates")
		self.ticker_dates = self.get_ticker_dates()

		print("Collecting Ticker Info")
		self.ticker_info = self.get_ticker_info()

		print("Collecting Interest Rates")
		self.rates = self.get_rates()

		print("Collecting Table Lengths")
		self.lengths = self.get_table_lengths()

		print("Generating Data Coordinates")
		self.generate_data_coords()

	def update(self):

		updated = False
		lengths = self.get_table_lengths()
		
		if lengths['options'] != self.lengths['options']:
		
			ticker_dates = self.get_ticker_dates(isUpdate=True)		
			for ticker in ticker_dates:

				if ticker not in self.ticker_dates:
					self.ticker_dates[ticker] = ticker_dates[ticker]
				elif ticker_dates[ticker][0] not in self.ticker_dates[ticker]:
					self.ticker_dates[ticker] = ticker_dates[ticker] + self.ticker_dates[ticker]

			self.lengths['options'] = lengths['options']
			updated = True

		if lengths['instruments'] != self.lengths['instruments']:

			self.ticker_info = self.get_ticker_info()
			self.lengths['instruments'] = lengths['instruments']
			updated = True

		if lengths['treasuryrates'] != self.lengths['treasuryrates']:

			self.rates = self.get_rates()
			self.lengths['treasuryrates'] = lengths['treasuryrates']
			updates = True

		if updated:
			self.generate_data_coords()

		return updated

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

	def read(self, query):

		tries = 0
		while tries < self.max_tries:
			try:
				conn = self.engine.connect()
				data = pd.read_sql(query, conn)
				conn.close()
				return data
			except Exception as e:
				print(e)
			tries += 1

		if tries >= self.max_tries:
			raise Exception("Too Many SQL Errors.")

	def write(self, table, df):

		tries = 0
		while tries < self.max_tries:
			try:
				conn = self.engine.connect()
				df.to_sql(table, conn, if_exists='append', index=False, chunksize=10_000)
				conn.close()
				break
			except Exception as e:
				print(e)
			tries += 1

		if tries >= self.max_tries:
			raise Exception("Too Many SQL Errors.")

	def get_scenarios(self, clauses):

		query = f"""
		    SELECT
		        t1.*,
		        ratemap.rate
		    FROM
		        (
		        SELECT
		            options.*,
		            ohlc.adj_close as stock_price,
		            ohlc.dividend_yield
		        FROM
		            options
		        JOIN
		            ohlc
		        ON
		            options.date_current = ohlc.date_current
		        AND options.ticker = ohlc.ticker
		        WHERE
		            {clauses}
		        ) as t1
		    JOIN
		        ratemap
		    ON
		        ratemap.date_current = t1.date_current
		    AND ROUND(t1.time_to_expiry * 365, 0) = ratemap.time_to_expiry
		"""
		return self.read(query)

	def get_password(self, username):

		query = f"""
			SELECT
				password
			FROM
				users
			WHERE
				username = "{username}"
		"""
		data = self.read(query)
		return data.password[0]

	def get_table_lengths(self):

		query = f"""
			SELECT
				TABLE_NAME,
				TABLE_ROWS
			FROM
				information_schema.tables
			WHERE
				TABLE_SCHEMA = "{CONFIG['db']}"
			AND
				TABLE_NAME in ("instruments", "treasuryrates", "options")
		"""
		data = self.read(query).set_index("TABLE_NAME")
		data = data.to_dict()
		return data['TABLE_ROWS']

	def get_ticker_info(self):

		query = """
			SELECT
				ticker,
				name,
				exchange_code,
				sector,
				industry
			FROM
				instruments
			ORDER BY
				market_cap DESC
		"""

		data = self.read(query)
		data = data.rename({"name" : "full_name"}, axis=1)
		data = data.drop_duplicates(subset=["ticker"])
		data = data.set_index("ticker").T.to_dict()
		return data

	def get_ticker_dates(self, isUpdate=False):

		where = ""
		if isUpdate:
			now = datetime.now() - timedelta(hours=self.HOUR_OFFSET)
			now = now.strftime("%Y-%m-%d")
			where = f'WHERE date_current = "{now}"'

		query = f"""
			SELECT
				ticker,
				date_current
			FROM
				tickerdates
			{where}
			ORDER BY
				ticker ASC,
				date_current DESC
		"""

		data = self.read(query).astype(str)
		data = data.groupby("ticker")["date_current"]
		data = data.apply(list).to_dict()
		return data

	def get_rates(self):

		date = datetime.now() - timedelta(days=7)
		date = date.strftime("%Y-%m-%d")

		query = f"""
			SELECT
				*
			FROM
				treasuryrates
			WHERE
				date_current >= "{date}"
		"""
		data = self.read(query)
		rates = list(data.iloc[-1, 1:].values / 100)
		rates = np.array([0] + rates)
		return rates

	def get_data(self, tickers, dates, table):

		if len(tickers) == 1:
			ticker_str = f'ticker = "{tickers[0]}"'
		else:
			tickers = tuple(tickers)
			ticker_str = f'ticker in {tickers}'

		if len(dates) == 1:
			date_str = f'date_current = "{dates[0]}"'
		else:
			dates = tuple(dates)
			date_str = f'date_current in {dates}'

		query = f"""
			SELECT
				*
			FROM
				{table}
			WHERE
				{ticker_str}
			AND
				{date_str}
		"""

		return self.read(query)

	def get_option_ids(self, tickers):

		if len(tickers) == 1:
			ticker_str = f'ticker = "{tickers[0]}"'
		else:
			tickers = tuple(tickers)
			ticker_str = f'ticker in {tickers}'

		query = f"""
			SELECT
				DISTINCT(option_id)
			FROM
				options
			WHERE
				{ticker_str}
			ORDER BY date_current, strike_price
		"""

		return self.read(query)

###################################################################################################

if __name__ == '__main__':

	print(Connector().get_option_ids(("TSLA", "AAPL")))