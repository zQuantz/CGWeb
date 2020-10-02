from scipy.stats import norm
import pandas as pd
import numpy as np

###################################################################################################

t_map = [
	0,
	30,
	60,
	90,
	180,
	12 * 30,
	24 * 30,
	36 * 30,
	60 * 30,
	72 * 30,
	120 * 30,
	240 * 30,
	360 * 30
]
t_map = np.array(t_map) / 360

###################################################################################################

def calculate_greeks(stock_price, div, options, r_map):

	if len(options) == 0:
		return options

	def get_rate(t):

		if t >= 30:
			return r_map[-1]
		
		b1 = t_map <= t
		b2 = t_map > t

		r1 = r_map[b1][-1]
		r2 = r_map[b2][0]

		t1 = t_map[b1][-1]
		t2 = t_map[b2][0]
		
		interpolated_rate = (t - t1) / (t2 - t1)
		interpolated_rate *= (r2 - r1)

		return interpolated_rate + r1

	time_to_expirations = options.time_to_expiry.unique()	
	unique_rates = {
		tte : get_rate(tte)
		for tte in time_to_expirations
	}

	options['rate'] = options.time_to_expiry.map(unique_rates)
	options['stock_price'] = stock_price
	options['dividend_yield'] = div

	###############################################################################################

	o = options.copy()
	m = o.option_type.map({"C" : 1, "P" : -1}).values

	tau = o.time_to_expiry.values
	rtau = np.sqrt(tau)
	iv = o.implied_volatility.values
	S = o.stock_price.values
	K = o.strike_price.values
	q = o.dividend_yield.values
	r = o.rate.values

	###################################################################################################

	eqt = np.exp(-q * tau)
	kert = K * np.exp(-r * tau)

	d1 = np.log(S / K)
	d1 += (r - q + 0.5 * (iv ** 2)) * tau
	d1 /= iv * rtau
	d2 = d1 - iv * rtau

	npd1 = norm.pdf(d1)
	ncd1 = norm.cdf(m * d1)
	ncd2 = norm.cdf(m * d2)

	###################################################################################################

	delta = m * eqt * ncd1

	gamma = np.exp(q - r) * npd1
	gamma /= (S * iv * rtau)

	vega = S * eqt * npd1 * rtau	
	vega /= 100

	rho = m * tau * kert * ncd2
	rho /= 100

	theta = (S * norm.pdf(m * d1) * iv)
	theta *= -eqt / (2 * rtau)
	theta -= m * r * kert * ncd2
	theta += m * q * S * eqt * ncd1
	theta /= 365

	###################################################################################################

	vanna = (vega / S)
	vanna *= (1 - d1 / (iv * rtau))

	vomma = (vega / iv) * (d1 * d2)

	charm = 2 * (r - q) * tau - d2 * iv * rtau
	charm /= 2 * tau * iv * rtau
	charm *= eqt * npd1
	charm = m * q * eqt * ncd1 - charm
	charm /= 365

	veta = q.copy()
	veta += ((r - q) * d1) / (iv * rtau)
	veta -= (1 + d1 * d2) / (2 * tau)
	veta *= -S * eqt * npd1 * rtau
	veta /= 365 * 100

	speed = 1
	speed += d1 / (iv * rtau)
	speed *= -gamma / S

	zomma = (d1 * d2 - 1) / iv
	zomma *= gamma

	color = 2 * (r - q) * tau
	color -= d2 * iv * rtau
	color *= d1 / (iv * rtau)
	color += 2 * q * tau + 1
	color *= -eqt * npd1 / (2 * S * tau * iv * rtau)
	color /= 365

	ultima = d1 * d2 * (1 - d1 * d2) + d1 * d1 + d2 * d2
	ultima *= -vega / (iv * iv)

	###################################################################################################

	options['delta'] = delta
	options['gamma'] = gamma
	options['theta'] = theta
	options['vega'] = vega
	options['rho'] = rho

	options['vanna'] = vanna
	options['vomma'] = vomma
	options['charm'] = charm
	options['veta'] = veta
	options['speed'] = speed
	options['zomma'] = zomma
	options['color'] = color
	options['ultima'] = ultima

	###################################################################################################

	options.loc[:, greek_cols] = options[greek_cols].replace([-np.inf, np.inf], np.nan)
	options.loc[:, greek_cols] = options[greek_cols].round(6).fillna(0)
	options = options.sort_values(["date_current", "option_type"], ascending=True)

	return options.drop(['stock_price', 'dividend_yield', 'rate'], axis=1)