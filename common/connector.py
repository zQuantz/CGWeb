from datetime import datetime, timedelta
import sqlalchemy as sql
import pandas as pd
import sys, os
import json

from common.const import CONFIG

###################################################################################################

class Connector():

	engine = sql.create_engine(CONFIG['db_address'])
	max_tries = 3

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

	def get_ticker_dates(self, days=60):

		dt = datetime.now() - timedelta(days=days)
		query = f"""
			SELECT
				ticker,
				date_current
			FROM
				options
			WHERE
				date_current >= "{dt.strftime("%Y-%m-%d")}"
			GROUP BY 
				ticker, date_current
			ORDER BY ticker ASC, date_current DESC
		"""

		data = self.read(query)
		data = data.sort_values(["ticker", "date_current"], ascending=[False, False])
		data = data.groupby("ticker").apply(lambda x:
			list(x.date_current.astype(str))
		)
		data = data.to_dict()
		return data

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

###################################################################################################
