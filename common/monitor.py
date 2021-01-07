from scipy.stats import percentileofscore
from bs4 import BeautifulSoup
import sqlalchemy as sql
from matplotlib import cm
import pandas as pd
import numpy as np
import json

from datetime import datetime, timedelta
import pandas_market_calendars as mcal

###################################################################################################

def bs(_str):
	return BeautifulSoup(_str, features="lxml")

def percentile(feature, lookback):
	
	def compute(x):
		_min = x.min()
		_max = x.max()
		return (x.values[-1] - _min) / (_max - _min)
	
	return feature.rolling(lookback, min_periods=int(lookback * TOL)).apply(compute)

def percentile_rank(feature, lookback):
	return feature.rolling(lookback, min_periods=int(lookback * TOL)).apply(
		lambda x: percentileofscore(x, x.values[-1])
	) / 100

def calculate_rv(x, days, min_days):
	x = np.log(x / x.shift()) ** 2
	x = x.rolling(days, min_periods=min_days).sum()
	return np.sqrt(x * (252 / days)) * 100

def background_color(pctile):

	if np.isnan(pctile):
		return f"background-color:white;"

	color = CMAP(pctile)
	color = [int(value * 255) for value in color]
	color[-1] = 0.65

	return f"background-color:rgba{str(tuple(color))};"

def color(value):

	if value < 0:
		color = "red"
	elif value > 0:
		color =  "green"
	else:
		color = "black"

	return f"color:{color};"

def format_table(key, data, formatters, styles):

	trs = ""
	tbody = bs("<tbody></tbody>").find("tbody")

	for category in TICKER_LISTS[key]:
		
		group = data[data.ticker.isin(TICKER_LISTS[key][category])]
		table = group.to_html(index=False, header=False, formatters=formatters)
		table = bs(table)

		for tr in table.find_all("tr"):

			tds = tr.find_all("td")
			ticker_styles = styles[tds[0].text]
			for i, td in enumerate(tds):
				td['style'] = ticker_styles[i]

			trs += f"{str(tr)}\n"
		
		trs += f"{str(BLANK_ROW)}\n"

	return bs(f"<tbody>{trs}</tbody>").find("tbody")

###################################################################################################

CMAP = cm.get_cmap("coolwarm_r")

DATE_FMT = "%Y-%m-%d"
S252 = np.sqrt(252)
D1 = "2019-01-01"
D2 = "2029-01-01"

TDAYS = mcal.date_range(
	mcal.get_calendar('NYSE').schedule(start_date=D1, end_date=D2),
	frequency="1D"
)
TDAYS = [str(day)[:10] for day in TDAYS]
tdays_df = pd.DataFrame(TDAYS, columns = ['date_current'])

TOL = 0.85

###################################################################################################

TICKER_LISTS = {
	"main" : {
		"Indices" : [
			"SPY", "QQQ", "DIA", "IWM", "VTI", "VEA", "FEZ", "EEM"
		],
		"Sectors" : [
			"XLE", "XOP", "XLV", "XLF", "XLK", "XLU", "XLY"
		],
		"Commodities" : [
			"GLD", "GDX", "SLV", "USO"
		],
		"Credit" : [
			"HYG", "TLT", "LQD"
		] ,
		"Big Tech" : [
			"AAPL", "MSFT", "AMZN", "GOOG", "FB", "TSLA", "BABA", "NVDA", "PYPL", "ADBE", "NFLX"
		]
	}, 
	"main_spreads" : {
		"Indices" : ["QQQ SPY", "IWM SPY", "EEM SPY", "QQQ IWM"],
		"Credit" : ["HYG SPY", "LQD SPY", "TLT SPY"]
	}
}

###################################################################################################

SINGLES_COL_ORDER = [
    "ticker",
    "name",
    "blank",
    "blank",
    "blank",
    "spot_price",
    "spot_daily_net_change",
    "spot_daily_pct_change",
    "spot_one_day_zscore",
    "spot_weekly_pct_change",
    "spot_monthly_pct_change",
    "spot_half_yearly_pct_change",
    "blank",
    "blank",
    "blank",
    "notional_flow",
    "rel_call_volume",
    "rel_put_volume",
    "rel_total_volume",
    "put_call_oi",
    "blank",
    "blank",
    "blank",
    "atm_iv",
    "atm_iv_percentile",
    "iv_daily_net_change",
    "iv_weekly_net_change",
    "rvol_term_one",
    "rvol_term_two",
    "vol_risk_premium",
    "blank",
    "blank",
    "blank",
    "down_skew",
    "up_skew",
    "full_skew",
    "term_structure"
]

SINGLES_PCT_COLS = [
    "spot_daily_pct_change",
    "spot_weekly_pct_change",
    "spot_monthly_pct_change",
    "spot_half_yearly_pct_change",
    "atm_iv",
    "iv_daily_net_change",
    "iv_weekly_net_change",
    "rvol_term_one",
    "rvol_term_two",
    "vol_risk_premium",
    "down_skew",
    "up_skew",
    "full_skew",
    "atm_iv_percentile",
    "term_structure"
]
SINGLES_DOL_COLS = [
    "spot_price",
    "spot_daily_net_change",
]
SINGLES_NON_FLOAT_COLS = [
    "blank",
    "ticker",
    "name"
]
SINGLES_FLOAT_COLS = [
    col for col in SINGLES_COL_ORDER
    if col not in
    SINGLES_NON_FLOAT_COLS + SINGLES_DOL_COLS + SINGLES_PCT_COLS
]

SINGLES_SIGN_COLS = [
    "spot_daily_net_change",
    "spot_daily_pct_change",
    "spot_weekly_pct_change",
    "spot_monthly_pct_change",
    "spot_half_yearly_pct_change",
    "iv_daily_net_change",
    "iv_weekly_net_change"
]
SINGLES_PCTILE_COLS = [
    "notional_flow",
    "put_call_oi",
    "vol_risk_premium",
    "down_skew",
    "up_skew",
    "full_skew",
    "term_structure"
]

SINGLES_FMTS = {
    col : "{:,.2f}$".format
    for col in SINGLES_DOL_COLS
}
SINGLES_FMTS.update({
    col : "{:,.2f}%".format
    for col in SINGLES_PCT_COLS
})
SINGLES_FMTS.update({
    col : "{:,.2f}".format
    for col in SINGLES_FLOAT_COLS
})
SINGLES_FMTS.update({
    "notional_flow" : "{:,.0f}M$".format
})

###################################################################################################

SPREADS_COL_ORDER = [
	"ticker",
	"blank",
	"blank",
	"blank",
	"spread",
	"term_one_daily_change",
	"term_one_weekly_change",
	"term_one_monthly_change",
	"term_one_rvol_spread",
	"term_one_carry",
	"term_one_zscore",
	"term_one_avg",
	"term_one_min",
	"term_one_max",
	"term_one_rank",
	"term_one_pct_rank",
	"term_one_corr3",
	"term_one_corr6",
	"blank",
	"blank",
	"blank",
	"spread2",
	"term_two_daily_change",
	"term_two_weekly_change",
	"term_two_monthly_change",
	"term_two_rvol_spread",
	"term_two_carry",
	"term_two_zscore",
	"term_two_avg",
	"term_two_min",
	"term_two_max",
	"term_two_rank",
	"term_two_pct_rank",
	"term_two_corr3",
	"term_two_corr6",
]

SPREADS_PCT_COLS = [
	"term_one_rank",
	"term_one_pct_rank",
	"term_one_corr3",
	"term_one_corr6",
	"term_two_rank",
	"term_two_pct_rank",
	"term_two_corr3",
	"term_two_corr6",
]
SPREADS_DOL_COLS = []
SPREADS_NON_FLOAT_COLS = [
	"ticker",
	"blank"
]
SPREADS_FLOAT_COLS = [
    col for col in SPREADS_COL_ORDER
    if col not in
    SPREADS_NON_FLOAT_COLS + SPREADS_DOL_COLS + SPREADS_PCT_COLS
]

SPREADS_SIGN_COLS = [
    "term_one_daily_change",
    "term_one_weekly_change",
    "term_one_monthly_change",
    "term_two_daily_change",
    "term_two_weekly_change",
    "term_two_monthly_change",
]
SPREADS_PCTILE_COLS = [
	"term_one_carry",
	"term_two_carry",
]
SPREADS_COLORED_COLS = [
	"term_one_corr3",
	"term_one_corr6",
	"term_one_rank",
	"term_one_pct_rank",
	"term_two_corr3",
	"term_two_corr6",
	"term_two_rank",
	"term_two_pct_rank",
]

SPREADS_FMTS = {
    col : "{:,.2f}$".format
    for col in SPREADS_DOL_COLS
}
SPREADS_FMTS.update({
    col : "{:,.2f}%".format
    for col in SPREADS_PCT_COLS
})
SPREADS_FMTS.update({
    col : "{:,.2f}".format
    for col in SPREADS_FLOAT_COLS
})

###################################################################################################

BLANK_ROW = pd.DataFrame([[""]*len(SINGLES_COL_ORDER)], columns = SINGLES_COL_ORDER)
BLANK_ROW = bs(BLANK_ROW.to_html(index=False, header=False))
BLANK_ROW = BLANK_ROW.find("tr")
BLANK_ROW['style'] = "height:1.5rem;"

###################################################################################################

class Monitor:

	def __init__(self, connector):

		self.connector = connector

	def singles(self, data):

		data['full_skew'] = data.down_skew + data.up_skew
		styles = {}
		def by_ticker(df):

			## Coordinates
			ticker = df.ticker.unique()[0]
			df = tdays_df.merge(df, on="date_current", how="outer")

			df['ticker'] = ticker
			df = df[df.date_current <= self.end_date]
			df = df.sort_values("date_current", ascending=True)

			df['name'] = self.connector.ticker_info[ticker]['full_name']
			styles[ticker] = [""]*len(SINGLES_COL_ORDER)

			## Spot Stats
			df['spot_daily_net_change'] = df.spot_price.diff()
			df['spot_daily_pct_change'] = df.spot_price.pct_change(1) * 100
			df['spot_weekly_pct_change'] = df.spot_price.pct_change(5) * 100
			df['spot_monthly_pct_change'] = df.spot_price.pct_change(21) * 100
			df['spot_half_yearly_pct_change'] = df.spot_price.pct_change(126) * 100
			
			## RVOL
			series = df.spot_daily_pct_change

			df['rvol_term_one'] = calculate_rv(df.spot_price, self.term_one, int(self.term_one * TOL))
			df['rvol_term_two'] = calculate_rv(df.spot_price, self.term_two, int(self.term_two * TOL))
			df['spot_one_day_zscore'] = (series * S252) / df.rvol_term_one
			
			## Flow
			cv = df.call_volume
			pv = df.put_volume
			tv = (cv + pv)
			
			df['notional_flow'] = (tv * 100 * df.spot_price) / 1e6
			df['rel_call_volume'] = cv / cv.rolling(20, min_periods=20 - 1).mean()
			df['rel_put_volume'] = pv / pv.rolling(20, min_periods=20 - 1).mean()
			df['rel_total_volume'] = tv / tv.rolling(20, min_periods=20 - 1).mean()
			df['put_call_oi'] = df.put_open_interest / df.call_open_interest
			
			## Volatility
			iv = df.atm_iv
			df['atm_iv_percentile'] = percentile(iv, self.lookback).values[-1] * 100
			df['iv_daily_net_change'] = iv.diff(1)
			df['iv_weekly_net_change'] = iv.diff(5)
			df['vol_risk_premium'] = df.atm_iv - df.rvol_term_one
			
			## Percentiles
			for col in SINGLES_PCTILE_COLS:
				
				pctile = percentile_rank(df[col], self.lookback).values[-1]
				styles[ticker][SINGLES_COL_ORDER.index(col)] += background_color(pctile)

			col = "spot_one_day_zscore"
			zscore = df[col].values[-1] + 3
			zscore /= 6
			styles[ticker][SINGLES_COL_ORDER.index(col)] += background_color(zscore)

			## Color coding
			for col in SINGLES_SIGN_COLS:

				value = df[col].values[-1]
				styles[ticker][SINGLES_COL_ORDER.index(col)] += color(value)
			
			return df.iloc[len(df) - 1, :]

		data = data.groupby("ticker").apply(by_ticker)
		
		data['blank'] = ' '
		data = data[SINGLES_COL_ORDER]
		return format_table(self.ticker_list, data, SINGLES_FMTS, styles)

	def spreads(self, data):

		cols = ['ticker', 'date_current', 'atm_iv', 'atm_iv2', 'spot_price']
		data = data[cols]

		pairs = [
			pair.split(" ")
			for category in TICKER_LISTS[self.ticker_list + "_spreads"]
			for pair in TICKER_LISTS[self.ticker_list + "_spreads"][category]
		]

		spread_dfs = []
		for pair in pairs:
			
			d1, d2 = data[data.ticker == pair[0]], data[data.ticker == pair[1]]
			spread_df = tdays_df.merge(d1, on="date_current", how="outer")
			spread_df = spread_df.merge(d2, on="date_current", how="outer")
			
			spread_df['ticker'] = " ".join(pair)
			spread_df['spread'] = spread_df.atm_iv_x - spread_df.atm_iv_y
			spread_df['spread2'] = spread_df.atm_iv2_x - spread_df.atm_iv2_y

			spread_dfs.append(spread_df)	

		data = pd.concat(spread_dfs).reset_index(drop=True)

		styles = {}
		def by_ticker(df):

			## Coordinates
			ticker = df.ticker.unique()[0]
			df = tdays_df.merge(df, on="date_current", how="outer")

			df['ticker'] = ticker
			df = df[df.date_current <= self.end_date]
			df = df.sort_values("date_current", ascending=True)

			styles[ticker] = [""]*len(SPREADS_COL_ORDER)

			values = zip(
				["one", "two"],
				[df.spread, df.spread2],
				[df.atm_iv_x, df.atm_iv2_x],
				[df.atm_iv_y, df.atm_iv2_y],
				[self.term_one, self.term_two]
			)

			for name, spread, aiv1, aiv2, term in values:

				df[f'term_{name}_daily_change'] = spread.diff(1)
				df[f'term_{name}_weekly_change'] = spread.diff(5)
				df[f'term_{name}_monthly_change'] = spread.diff(21)

				window = spread.rolling(self.lookback, min_periods=self.tolerance)
				df[f'term_{name}_avg'] = window.mean()
				df[f'term_{name}_min'] = window.min()
				df[f'term_{name}_max'] = window.max()
				df[f'term_{name}_rank'] = percentile(spread, self.lookback) * 100
				df[f'term_{name}_pct_rank'] = percentile_rank(spread, self.lookback) * 100
				df[f'term_{name}_zscore'] = (spread - window.mean()) / window.std()

				df[f'term_{name}_corr3'] = aiv1.rolling(63, min_periods = int(63 * TOL)).corr(aiv2) * 100
				df[f'term_{name}_corr6'] = aiv1.rolling(126, min_periods = int(126 * TOL)).corr(aiv2) * 100

				spot_x, spot_y = df.spot_price_x, df.spot_price_y
				
				rv_spread = calculate_rv(spot_x, term, int(term * TOL))
				rv_spread -= calculate_rv(spot_y, term, int(term * TOL))
				df[f'term_{name}_rvol_spread'] = rv_spread

			df['term_one_carry'] = df.spread - df.term_one_rvol_spread
			df['term_two_carry'] = df.spread2 - df.term_two_rvol_spread

			col = "term_one_zscore"
			zscore = df[col].values[-1] + 3
			zscore /= 6
			styles[ticker][SPREADS_COL_ORDER.index(col)] += background_color(zscore)

			col = "term_two_zscore"
			zscore = df[col].values[-1] + 3
			zscore /= 6
			styles[ticker][SPREADS_COL_ORDER.index(col)] += background_color(zscore)

			## Color coding
			for col in SPREADS_SIGN_COLS:

				value = df[col].values[-1]
				styles[ticker][SPREADS_COL_ORDER.index(col)] += color(value)

			## Percentiles
			for col in SPREADS_PCTILE_COLS:
				
				pctile = percentile_rank(df[col], self.lookback).values[-1]
				styles[ticker][SPREADS_COL_ORDER.index(col)] += background_color(pctile)

			for col in SPREADS_COLORED_COLS:
				
				value = df[col].values[-1]
				styles[ticker][SPREADS_COL_ORDER.index(col)] += background_color(value / 100)

			return df.iloc[len(df) - 1, :]

		data = data.groupby("ticker").apply(by_ticker)
		data = data.sort_values("date_current")

		data['blank'] = ' '
		data = data[SPREADS_COL_ORDER]
		return format_table(self.ticker_list + "_spreads", data, SPREADS_FMTS, styles)

	def calculate_monitor(self, ticker_list, term_one, term_two, down_strike, up_strike, lookback, end_date):

		tickers = [
			ticker
			for category in TICKER_LISTS[ticker_list]
			for ticker in TICKER_LISTS[ticker_list][category]
		]

		term_one = int(term_one)
		term_two = int(term_two)
		down_strike = int(down_strike)
		up_strike = int(up_strike)
		lookback = int(lookback)

		query = f"""
			SELECT
				ao.*,
				o.adjclose_price AS spot_price,
				zs.m{term_one}m100 AS atm_iv,
				zs.m{term_two}m100 AS atm_iv2,
				zs.m{term_two}m100 - zs.m{term_one}m100 AS term_structure,
				zs.m{term_one}m{down_strike} - zs.m{term_one}m100 AS down_skew,
				zs.m{term_one}m100 - zs.m{term_one}m{up_strike} AS up_skew
			FROM
				ohlc AS o
			LEFT JOIN
				aggoptionstats AS ao
				USING(date_current, ticker)
			LEFT JOIN
				zsurface AS zs
				USING(date_current, ticker)
			WHERE
				ticker IN {str(tuple(tickers))}
			AND date_current <= "{end_date}"
		"""
		data = self.connector.read(query)
		data['date_current'] = data.date_current.astype(str)

		term_one *= 21
		term_two *= 21
		lookback *= 21

		self.term_one = term_one
		self.term_two = term_two
		self.lookback = lookback
		self.down_strike = down_strike
		self.up_strike = up_strike
		self.end_date = end_date
		self.ticker_list = ticker_list
		self.tolerance = int(self.lookback * TOL)

		self._data = {
			"singles" : self.singles(data),
			"spreads" : self.spreads(data)
		}
