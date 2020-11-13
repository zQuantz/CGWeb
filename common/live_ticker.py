from common.const import DIR, CONVERTER, NUMBERS, CONFIG
from common.greeks import calculate_greeks
from common.utils.request import request

from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import itertools
import sys, os
import time

###################################################################################################

ANALYSIS = "https://ca.finance.yahoo.com/quote/{ticker}/analysis?p={ticker}"
STATS = "https://finance.yahoo.com/quote/{ticker}/key-statistics?p={ticker}"
OPTIONS = "https://finance.yahoo.com/quote/{ticker}/options?p={ticker}"
OHLC = "https://finance.yahoo.com/quote/{ticker}/history"
SUMMARY = "https://finance.yahoo.com/quote/{ticker}/"
PARSER = "lxml"

NAMED_DATE_FMT = "%B %d, %Y"

OPTION_COLS = [
	"date_current",
	"ticker",
	"expiration_date",
	"days_to_expiry",
	"option_type",
	"strike_price",
	"bid_price",
	"option_price",
	"ask_price",
	"implied_volatility",
	"volume",
	"open_interest"
]

OHLC_COLS = [
	"date_current",
	"ticker",
	"open_price",
	"high_price",
	"low_price",
	"close_price",
	"adjclose_price",
	"volume",
	"dividend_yield",
]

###################################################################################################

class LiveTicker():

	def __init__(self, ticker):

		self.ticker = ticker

		try:
			self.div = self.get_dividends()
			print(f"{ticker},Dividend,Success,")
		except Exception as e:
			print(f"{ticker},Dividend,Failure,{e}")
			raise Exception("Dividend")
		self.sleep()

		try:
			self.get_ohlc()
			print(f"{ticker},OHLC,Success,")
		except Exception as e:
			print(f"{ticker},OHLC,Failure,{e}")
			raise Exception("OHLC")
		self.sleep()

		try:
			self.get_keystats()
			print(f"{ticker},Key Stats,Success,")
		except Exception as e:
			self.keystats = pd.DataFrame(columns = ["feature", "modifier", "value"])
			print(f"{ticker},Key Stats,Failure,{e}")
		self.sleep()

		try:
			self.options = []
			self.get_options()
			print(f"{ticker},Options,Success,")	
		except Exception as e:
			print(f"{ticker},Options,Failure,{e}")
			raise Exception("Options")
		self.sleep()

	def sleep(self):

		time.sleep(0.25)

	def fmt(self, str_, metric=''):

		try:
			date = datetime.strptime(str_, "%b %d, %Y")
			return date.strftime("%Y-%m-%d")
		except Exception as e:
			pass

		default_value = '' if 'Date' in metric else '' if 'Factor' in metric else 0

		if ':' in str_:
			return str_
		
		if str_ in ['', 'N/A', '∞']:
			return None
		
		str_ = str_.replace(',', '').replace('$', '')

		modifier = str_[-1]
		if modifier in NUMBERS:
			return np.round(float(str_), 5)
		
		if modifier == '%':
			return np.round(float(str_[:-1]) / 100, 5)
		
		if modifier in ['M', 'B', 'T']:
			return np.round(float(str_[:-1]) * CONVERTER[modifier], 5)

	def option_fmt(self, str_number, metric=''):
	
		if str_number == '':
			return 0

		if str_number == 'N/A':
			return 0

		for token in ',$%':
			str_number = str_number.replace(token, '')

		return float(str_number.replace('-', '0'))

	def feature_conversion(self, str_):

		str_ = str_.split()
		if str_[-1] in NUMBERS:
			str_ = str_[:-1]
		str_ = ' '.join(str_)
		
		if '(' in str_:
			modifier = str_[str_.find('(')+1:str_.rfind(')')]
			feature_name = str_.split('(')[0]
			return (feature_name.strip(), modifier)
		else:
			return (str_, '')

	def get_dividends(self):

		url = SUMMARY.format(ticker = self.ticker)
		bs = BeautifulSoup(request(CONFIG, url).content, PARSER)

		table = bs.find_all("table")[1]
		div = table.find("td", {"data-test" : "DIVIDEND_AND_YIELD-value"})

		if not div:
			div = table.find("td", {"data-test" : "TD_YIELD-value"}).text
		else:
			div = div.text.split(' ')[1][1:-1]
			div = div.replace('N/A', '')

		return self.option_fmt(div, 'Dividend')

	def get_ohlc(self):

		url = OHLC.format(ticker = self.ticker)
		bs = BeautifulSoup(request(CONFIG, url).content, PARSER)

		prices = bs.find("table", {"data-test" : "historical-prices"})
		prices = prices.find_all("tr")[1]
		prices = [price.text for price in prices]

		self.ohlc_date = datetime.strptime(prices[0], "%b %d, %Y").strftime("%Y-%m-%d")

		prices = list(map(self.option_fmt, prices[1:], OHLC_COLS[:-2]))
		prices = [self.ohlc_date, self.ticker] + prices + [self.div]
		self.adj_close = prices[-3]
		self.ohlc = pd.DataFrame([prices], columns = OHLC_COLS)

	def get_options(self):

		def append_options(table, expiry_date_fmt, expiration_days, option_type):

			for row in table.find_all("tr")[1:]:
				es = [e for e in row.find_all("td")[2:]]
				self.options.append([
						self.ohlc_date,
						self.ticker,
						expiry_date_fmt,
						expiration_days,
						option_type,
						self.option_fmt(es[0].text, 'Strike Price'),
						self.option_fmt(es[2].text, 'Bid'),
						self.option_fmt(es[1].text, 'Option Price'),
						self.option_fmt(es[3].text, 'Ask'),
						self.option_fmt(es[-1].text, 'Implied Volatility'),
						self.option_fmt(es[-2].text, 'Volume'),
						self.option_fmt(es[-3].text, 'Open Interest')
					])

		def get_page(url):

			ctr, max_ctr = 0, 3
			while (ctr < max_ctr):	
				
				bs = BeautifulSoup(request(CONFIG, url).content, PARSER)
				options = bs.find_all("option")

				if len(options) != 0:
					break

				ctr += 1
				print(f"{self.ticker},Option Download,{ctr}")
				self.sleep()

			return bs, options

		url = OPTIONS.format(ticker = self.ticker)
		bs, options = get_page(url)

		for option in options:

			self.sleep()

			expiry, expiry_date = option.get("value"), option.text
			print(f"{self.ticker},Option Expiry,{expiry},{expiry_date.replace(',', '.')}")
			
			expiry_date = datetime.strptime(expiry_date, NAMED_DATE_FMT)
			expiry_date_fmt = expiry_date.strftime("%Y-%m-%d")
			expiration_days = (expiry_date - datetime.now()).days + 1

			page = url+f"&date={str(expiry)}"
			bs, _ = get_page(page)

			calls = bs.find("table", {"class" : "calls"})
			puts = bs.find("table", {"class" : "puts"})
			
			if calls:
				append_options(calls, expiry_date_fmt, expiration_days, 'C')
			
			if puts:
				append_options(puts, expiry_date_fmt, expiration_days, 'P')

		df = pd.DataFrame(self.options, columns = OPTION_COLS)
		oid = df.ticker + ' ' + df.expiration_date + ' ' + df.option_type
		sp = df.strike_price.round(2).astype(str)
		sp = sp.str.rstrip("0").str.rstrip(".")
		df['option_id'] = oid + sp

		self.options = df

	def get_keystats(self):

		def get_items(bs, text):

			span = bs.find("span", text=text)
			main_div = span.parent.parent

			items = []
			for tr in main_div.find_all("tr"):
				
				tds = tr.find_all("td")
				if len(tds) == 0:
					continue

				items.append([tds[0].text, tds[1].text])

			return items

		url = STATS.format(ticker = self.ticker)
		bs = request(CONFIG, url).content
		bs = BeautifulSoup(bs, PARSER)

		items = get_items(bs, "Financial Highlights")
		items.extend(get_items(bs, "Trading Information"))
		items.extend(get_items(bs, "Valuation Measures"))

		key_stats = []
		for feature_name, feature in items:
			key = self.feature_conversion(feature_name)
			key_stats.append([
				*key,
				self.fmt(feature, metric = key[0])
			])

		df = pd.DataFrame(key_stats, columns = ["feature", "modifier", "value"])
		pkey = ["feature", "modifier"]
		df.loc[:, pkey] = df[pkey].fillna('')
		self.keystats = df