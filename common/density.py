from common.greeks import calculate_greeks
from scipy.stats import norm
import pandas as pd
import numpy as np
import sys, os

class Density:

	def __init__(self, connector):

		self.reset()
		self.connector = connector

	def reset(self):

		self.data = None
		self.symbol = None
		self.ticker = None

	def calculate_risk_neutral_density(self, data, otype):

		def find_rnd(exp):
			
			if otype == "C":
				rnd = [
					exp.kprime.values[0] - p
					for p in exp.kprime
				]
			else:
				rnd = [
					p - exp.kprime.values[0]
					for p in exp.kprime
				]
			rnd = pd.Series(rnd)
			rnd = rnd.rolling(5, min_periods=1).median()
			rnd = rnd.diff()

			if rnd.min() < 0:
				rnd = rnd + abs(rnd.min())
			rnd = rnd / rnd.sum()

			_strikes = pd.DataFrame()
			_strikes['rnd'] = rnd
			_strikes['strike_price'] = exp.strike_price.values
			_strikes = strikes.merge(_strikes, on="strike_price", how="outer")
			_strikes = _strikes.fillna(0)

			return _strikes

		data = data[data.option_type == otype]

		S = data.stock_price.values
		K = data.strike_price.values
		q = np.log(1 + data.dividend_yield / 100).values
		r = np.log(1 + data.rate).values
		v = data.implied_volatility.values / 100
		T = (data.days_to_expiry / 252).values

		d2 = np.log(S / K) + (r - q - 0.5 * v * v) * T
		d2 /= np.sqrt(T) * v
		d2 *= 1 if otype == "C" else -1
		nd2 = norm.cdf(d2)
		data['d2'] = d2
		data['nd2'] = nd2
		data['ert'] = np.exp(-r * T)
		data['kprime'] = (data.nd2 * data.ert).values

		data = data[data.days_to_expiry < 400]
		data = data[data.days_to_expiry > 10]
		data = data[data.implied_volatility > 0]
		
		spu = data.strike_price.unique()
		spmin = (int(spu.min() / 5) * 5)
		spmax = (int(spu.max() / 5) * 5)
		
		strikes = data.strike_price.sort_values().unique()
		strikes = pd.DataFrame(strikes, columns = ['strike_price'])
		bins = list(range(spmin, spmax, 5))
		
		strikes = data.strike_price.sort_values().unique()
		strikes = pd.DataFrame(strikes, columns = ['strike_price'])
		
		rnds = data.groupby("expiration_date").apply(find_rnd)
		rnds = rnds.reset_index(level=0).reset_index(drop=True)
		rnds['bins'] = pd.cut(rnds.strike_price, bins)
		rnds = rnds.groupby(["expiration_date", "bins"])
		rnds = rnds.apply(lambda x: x['rnd'].sum())
		rnds = rnds.reset_index(name="rnd")
		rnds = rnds.pivot(*rnds.columns)
		
		bins = np.array(bins) / data.stock_price.values[0]
		bins = bins * 100
		X, Y = np.meshgrid(
			bins[:rnds.shape[1]],
			data.days_to_expiry.unique()
		)
		Z = rnds.values

		return {
			"X" : X.tolist(),
			"Y" : Y.tolist(),
			"Z" : Z.tolist()
		}

	def get_risk_neutral_density(self, ticker, date):

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
		
		start = str(data.date_current.values[0])
		end = f"{int(start[:4])+5}{start[4:]}"

		fridays = pd.date_range(start, end, freq="WOM-3FRI").astype(str)
		thursdays = pd.date_range(start, end, freq="WOM-3THU").astype(str)

		regulars = list(fridays) + list(thursdays)
		data = data[data.expiration_date.astype(str).isin(regulars)]
		data = data.reset_index(drop=True)

		moneyness = abs(data.stock_price / data.strike_price - 1)
		data = data[moneyness <= 0.35]

		self.data = {
			"C" : self.calculate_risk_neutral_density(data, "C"),
			"P" : self.calculate_risk_neutral_density(data, "P")
		}

if __name__ == '__main__':

	pass
