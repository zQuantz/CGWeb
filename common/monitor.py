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
	
	return feature.rolling(lookback, min_periods=int(lookback * 0.90)).apply(compute)

def percentile_rank(feature, lookback):
	return feature.rolling(lookback, min_periods=int(lookback * 0.90)).apply(
		lambda x: percentileofscore(x, x.values[-1])
	) / 100

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
	}
}

COL_ORDER = [
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
PCT_COLS = [
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
    "term_structure"
]
DOL_COLS = [
    "spot_price",
    "spot_daily_net_change",
]
NON_FLOAT_COLS = [
    "blank",
    "ticker",
    "name"
]
FLOAT_COLS = [
    col for col in COL_ORDER
    if col not in
    NON_FLOAT_COLS + DOL_COLS + PCT_COLS
]

SIGN_COLS = [
    "spot_daily_net_change",
    "spot_daily_pct_change",
    "spot_weekly_pct_change",
    "spot_monthly_pct_change",
    "spot_half_yearly_pct_change",
    "iv_daily_net_change",
    "iv_weekly_net_change"
]
PCTILE_COLS = [
    "notional_flow",
    "put_call_oi",
    "vol_risk_premium",
    "down_skew",
    "up_skew",
    "full_skew",
    "term_structure"
]

FMTS = {
    col : "{:,.2f}$".format
    for col in DOL_COLS
}
FMTS.update({
    col : "{:,.2f}%".format
    for col in PCT_COLS
})
FMTS.update({
    col : "{:,.2f}".format
    for col in FLOAT_COLS
})
FMTS.update({
    "notional_flow" : "{:,.0f}M$".format
})

BLANK_ROW = pd.DataFrame([[""]*len(COL_ORDER)], columns = COL_ORDER)
BLANK_ROW = bs(BLANK_ROW.to_html(index=False, header=False))
BLANK_ROW = BLANK_ROW.find("tr")
BLANK_ROW['style'] = "height:1.5rem;"

###################################################################################################

class Monitor:

	def __init__(self, connector):

		self.connector = connector

	def calculate_monitor(self, ticker_list, term_one, term_two, down_strike, up_strike, lookback, end_date):

		tickers = [
			ticker
			for category in TICKER_LISTS[ticker_list]
			for ticker in TICKER_LISTS[ticker_list][category]
		]

		self.tickers = tickers
		self.term_one = term_one
		self.term_two = term_two
		self.down_strike = up_strike
		self.lookback = lookback
		self.end_date = end_date

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
			INNER JOIN
				aggoptionstats AS ao
				USING(date_current, ticker)
			INNER JOIN
				zsurface AS zs
				USING(date_current, ticker)
			WHERE
				ticker IN {str(tuple(tickers))}
		"""
		data = self.connector.read(query)
		data['date_current'] = data.date_current.astype(str)
		data['full_skew'] = data.down_skew + data.up_skew

		term_one *= 21
		term_two *= 21
		lookback *= 21

		data = tdays_df.merge(data, on="date_current", how="outer")
		data = data.dropna(subset=["ticker"])
		data = data[data.date_current <= end_date]
		data = data.sort_values("date_current", ascending=True)

		styles = {}

		def by_ticker(df):

			## Coordinates
			ticker = df.ticker.values[0]
			df['name'] = self.connector.ticker_info[ticker]['full_name']
			styles[ticker] = [""]*len(COL_ORDER)

			## Spot Stats
			df['spot_daily_net_change'] = df.spot_price.diff()
			df['spot_daily_pct_change'] = df.spot_price.pct_change(1) * 100
			df['spot_weekly_pct_change'] = df.spot_price.pct_change(5) * 100
			df['spot_monthly_pct_change'] = df.spot_price.pct_change(21) * 100
			df['spot_half_yearly_pct_change'] = df.spot_price.pct_change(126) * 100
			
			## RVOL
			series = df.spot_daily_pct_change

			df['rvol_term_one'] = series.rolling(term_one, min_periods=term_one).std() * S252
			df['rvol_term_two'] = series.rolling(term_two, min_periods=term_two).std() * S252
			df['spot_one_day_zscore'] = (series * S252) / df.rvol_term_one
			
			## Flow
			cv = df.call_volume
			pv = df.put_volume
			tv = (cv + pv)
			
			df['notional_flow'] = (tv * 100 * df.spot_price) / 1e6
			df['rel_call_volume'] = cv / cv.rolling(20, min_periods=20).mean()
			df['rel_put_volume'] = pv / pv.rolling(20, min_periods=20).mean()
			df['rel_total_volume'] = tv / tv.rolling(20, min_periods=20).mean()
			df['put_call_oi'] = df.put_open_interest / df.call_open_interest
			
			## Volatility
			iv = df.atm_iv
			df['iv_daily_net_change'] = iv.diff(1)
			df['iv_weekly_net_change'] = iv.diff(5)
			df['vol_risk_premium'] = df.atm_iv - df.rvol_term_one
			
			## Percentiles
			for col in PCTILE_COLS:
				
				pctile = percentile_rank(df[col], lookback).values[-1]
				styles[ticker][COL_ORDER.index(col)] += background_color(pctile)

			col = "spot_one_day_zscore"
			zscore = df[col].values[-1] + 3
			zscore /= 6
			styles[ticker][COL_ORDER.index(col)] += background_color(zscore)

			## Color coding
			for col in SIGN_COLS:

				value = df[col].values[-1]
				styles[ticker][COL_ORDER.index(col)] += color(value)
			
			return df.iloc[len(df) - 1, :]

		data = data.groupby("ticker").apply(by_ticker)
		data['blank'] = ' '
		data = data[COL_ORDER]

		tbody = bs("<tbody></tbody>").find("tbody")
		trs = ""
		for category in TICKER_LISTS[ticker_list]:
			
			group = data[data.ticker.isin(TICKER_LISTS[ticker_list][category])]
			table = group.to_html(index=False, header=False, formatters=FMTS)
			table = bs(table)

			for tr in table.find_all("tr"):

				tds = tr.find_all("td")
				ticker_styles = styles[tds[0].text]
				for i, td in enumerate(tds):
					td['style'] = ticker_styles[i]

				trs += f"{str(tr)}\n"
			
			trs += f"{str(BLANK_ROW)}\n"

		self._data = bs(f"<tbody>{trs}</tbody>").find("tbody")
