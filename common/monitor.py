from scipy.stats import percentileofscore
import sqlalchemy as sql
import pandas as pd
import numpy as np
import json

from datetime import datetime, timedelta
import pandas_market_calendars as mcal

###################################################################################################

DATE_FMT = "%Y-%m-%d"
S252 = np.sqrt(252)
D1 = "2019-01-01"
D2 = "2029-01-01"

TDAYS = mcal.date_range(
	mcal.get_calendar('NYSE').schedule(start_date=min_date, end_date=max_date),
	frequency="1D"
)
TDAYS = [str(day)[:10] for day in TDAYS]
tdays_df = pd.DataFrame(TDAYS, columns = ['date_current'])

###################################################################################################

def percentile(feature):
	
	def compute(x):
		_min = x.min()
		_max = x.max()
		return 100 * (x.values[-1] - _min) / (_max - _min)
	
	return feature.rolling(lookback, min_periods=lookback).apply(compute)

def percentile_rank(feature):
	return feature.rolling(lookback, min_periods=lookback).apply(
		lambda x: percentileofscore(x, x.values[-1])
	)

class Monitor:

	def __init__(self, connector):

		self.connector = connector

	def calculate_monitor(self, tickers, term_one, term_two, down_strike, up_strike, lookback, end_date):

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
		_data['date_current'] = _data.date_current.astype(str)
		data['full_skew'] = data.down_skew + data.up_skew

		term_one *= 21
		term_two *= 21
		lookback *= 21

		data = tdays_df.merge(_data, on="date_current", how="outer")
		data = data.dropna(subset=["ticker"])
		data = data[data.date_current <= end_date]
		data = data.sort_values("date_current", ascending=True)

		def by_ticker(df):

			## Coordinates
			ticker = df.ticker.values[0]
			df['name'] = self.connector.ticker_info[ticker]['name']
	
			## Spot Stats
			ticker['spot_daily_net_change'] = df.spot_price.diff()
			df['spot_daily_pct_change'] = df.spot_price.pct_change(1) * 100
			df['spot_weekly_pct_change'] = df.spot_price.pct_change(5) * 100
			df['spot_monthly_pct_change'] = df.spot_price.pct_change(21) * 100
			df['spot_half_yearly_pct_change'] = df.spot_price.pct_change(126) * 100
			
			## RVOL
			series = df.spot_daily_pct_change

			df['rvol_term_one'] = series.rolling(term_one, min_periods=term_one).std() * S252
			df['rvol_term_two'] = series.rolling(term_two, min_periods=term_two).std() * S252
			df['one_day_zscore'] = (series * S252) / df.rvol_term_one
			
			## Flow
			cv = df.call_volume
			pv = df.put_volume
			tv = (cv + pv)
			
			df['notional_flow'] = (tv * 100 * df.spot_price) / 1e6
			df['call_volume_flag'] = cv / cv.rolling(20, min_periods=20).mean()
			df['put_volume_flag'] = pv / pv.rolling(20, min_periods=20).mean()
			df['option_volume_flag'] = tv / tv.rolling(20, min_periods=20).mean()
			df['put_call_oi'] = df.put_open_interest / df.call_open_interest
			
			## Volatility
			iv = df.atm_iv
			df['iv_daily_net_change'] = iv.diff(1)
			df['iv_weekly_net_change'] = iv.diff(5)
			df['vol_risk_premium'] = df.atm_iv - df.rvol_term_one
			
			## Percentiles
			f = df.rvol_term_one
			df['rvol_term_one_percentile'] = percentile(df.rvol_term_one)
			df['rvol_term_two_percentile'] = percentile(df.rvol_term_two)
			df['atm_iv_percentile'] = percentile(df.atm_iv)
			df['term_structure_percentile'] = percentile(df.term_structure)
			df['full_skew_percentile'] = percentile(df.full_skew)
			
			return df

		stats = data.groupby("ticker").apply(by_ticker)

