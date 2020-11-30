from sklearn.linear_model import LinearRegression
from common.greeks import calculate_greeks
import pandas as pd
import numpy as np
import sys, os

class Surface:

	def __init__(self, connector):

		self.reset()
		self.connector = connector

	def reset(self):

		self.data = None
		self.symbol = None
		self.ticker = None

	def calculate_implied_forward(self, data):

		def forward_price(exp):
			
			y = (exp.mid_price_x - exp.mid_price_y).values
			ya = abs(y)
			yte = exp.days_to_expiry.values[0] / 365
			r = exp.rate.values[0]

			F = exp.iloc[ya.argmin()].strike_price
			F += np.exp(-r * yte) * y[ya.argmin()]
			return F

		cols = ['strike_price', 'mid_price', 'days_to_expiry', 'rate', 'stock_price']
		c = data[data.option_type == "C"][cols]
		p = data[data.option_type == "P"][cols[:3]]

		pc = c.merge(p, on=["days_to_expiry", "strike_price"], how="inner")
		pc = pc.groupby("days_to_expiry").apply(forward_price).reset_index()
		pc.columns = ['days_to_expiry', 'forward_price']

		return data.merge(pc, on="days_to_expiry", how="inner")

	def calculate_surface(self, data):

		sp = data.stock_price.values[0]
		K = np.arange(sp * 0.75, sp * 1.25, sp / 100)

		def fit_regression(exp):

			c = exp[exp.option_type == "C"].reset_index(drop=True)
			p = exp[exp.option_type == "P"].reset_index(drop=True)
			
			civ = c.iloc[c.otm.argmax()].implied_volatility
			piv = p.iloc[p.otm.argmax()].implied_volatility
			adj_factor = piv - (piv + civ) * 0.5
			
			c['implied_volatility'] = (c.implied_volatility + adj_factor)
			p['implied_volatility'] = (p.implied_volatility - adj_factor)
			exp = pd.concat([c, p]).reset_index(drop=True)
			exp = exp.sort_values("strike_price")
			
			x = np.log(exp.strike_price / exp.forward_price)
			xx = x * x
			y = (exp.implied_volatility) ** 2

			lr = LinearRegression()
			lr = lr.fit(np.array([xx, x]).T, y, sample_weight=exp.vega.values)
			ivmin = exp.iloc[abs(x).argmin()].implied_volatility ** 2

			if lr.coef_[0] < 0:
				print(lr.coef_)
				return
				
			xx = np.log(K / exp.forward_price.values[0]) ** 2
			y = lr.coef_[0] * xx + ivmin

			return pd.Series(y)

		V = data.groupby("days_to_expiry").apply(fit_regression).dropna()
		T = data.years.unique()
		return T, K, V

	def calculate_features(self, data):

		## Calculate Features
		data['years'] = data.days_to_expiry / 365
		data['moneyness'] = data.strike_price / data.stock_price
		data['mid_price'] = ((data.bid_price + data.ask_price) * 0.5).values
		
		data['otm'] = data.stock_price - data.strike_price
		data['otm'] = data.otm * data.option_type.map({"C" : 1, "P" : -1})

		return data

	def pre_filter(self, data):

		## Filter for regular expirations
		start = str(data.date_current.values[0])
		end = f"{int(start[:4])+5}{start[4:]}"

		fridays = pd.date_range(start, end, freq="WOM-3FRI").astype(str)
		thursdays = pd.date_range(start, end, freq="WOM-3THU").astype(str)

		regulars = list(fridays) + list(thursdays)
		data = data[data.expiration_date.astype(str).isin(regulars)]
		data = data.reset_index(drop=True)

		## Filter bad data
		data = data[abs(data.moneyness - 1) < 0.4]
		data = data[data.bid_price != 0]
		data = data[data.ask_price != 0]
		data = data[data.implied_volatility != 0]
		data = data[data.days_to_expiry > 10]
		data = data[data.days_to_expiry < 550]

		return data

	def post_filter(self, data):

		x = data.days_to_expiry.value_counts()
		x = x[x >= 50]
		data = data[data.days_to_expiry.isin(x.index)]
		data = data[data.otm < 0]

		return data

	def get_surface(self, ticker, date):

		if not ticker or not date:
			self.reset()
			return

		self.ticker = ticker
		self.date = date

		self.symbol = self.connector.ticker_info[ticker]['exchange_code']
		self.symbol += f":{ticker}"
		self.symbol = {
			"ticker" : ticker,
			"symbol" : self.symbol
		}

		data = self.connector.get_options(ticker, date)
		data = self.calculate_features(data)
		data = self.pre_filter(data)
		data = self.calculate_implied_forward(data)
		data = self.post_filter(data)

		if (data.days_to_expiry.nunique() < 5):
			return

		data = calculate_greeks(data)
		data['implied_volatility'] = data.implied_volatility / 100
		data = data.dropna().reset_index(drop=True)

		T, K, V = self.calculate_surface(data)

		K /= data.stock_price.values[0] * 0.01
		T *= 365
		V = np.sqrt(V).values * 100

		K = np.round(K, 2)
		T = np.round(T, 0)
		V = np.round(V, 2)

		K, T = np.meshgrid(K, T)
		T = T.copy()
		K = K.copy()

		self.data = {
			"X" : T.tolist(),
			"Y" : K.tolist(),
			"Z" : V.tolist(),
			"xmin" : int(T[:, 0].min() * -2),
			"xmax" : int(T[:, 0].max() * 1.15),
			"ymin" : int(K[0, :].min() * 0.90),
			"ymax" : int(K[0, :].max() * 1.10),
			"zmin" : int(V.min() * 0.9),
			"zmax" : int(V.max() * 1.1)
		}

if __name__ == '__main__':

	s = Surface(None)
	s.get_surface("AAPL", "AAPL")
