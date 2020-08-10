from itertools import product
from scipy.stats import norm
import pandas as pd
import numpy as np
import sys, os

###################################################################################################

columns = [
	"stock_price",
	"strike_price",
	"implied_volatility",
	"time_to_expiry",
	"rate",
	"dividend_yield"
]

greek_columns = [
	'delta',
	'gamma',
	'theta',
	'vega',
	'rho',
	'vanna',
	'vomma',
	'charm',
	'veta',
	'speed',
	'zomma',
	'color',
	'ultima'
]

display_columns = [
	" ".join(map(str.capitalize, col.split("_")))
	for col in columns + ["option_type"] + greek_columns
]

###################################################################################################

empty_table = pd.DataFrame([], columns = display_columns)
empty_table = empty_table.to_html(classes=["table table-sm table-hover table-borderless"])

maxi = 0.01
mini = 0.01
n_increments = (maxi * 100) / mini

increments = np.arange(-mini * n_increments + mini, mini * n_increments + 2 * mini, mini)
increments = increments.reshape(-1, 1)

n_variables = 6

###################################################################################################

def process(value, factor=1):

    if "," in value:
        return [float(v) / factor for v in value.split(",")]
    elif ":" in value:
        s, e, j = [float(v) / factor for v in value.split(":")]
        return np.arange(s, e + j, j).tolist()
    else:
        return [float(value) / factor]

def calculate_greeks(args):

	S = process(args.get("S"))
	K = process(args.get("K"))
	IV = process(args.get("IV"), 100)
	T = process(args.get("t"), 365)
	r = process(args.get("r"), 100)
	q = process(args.get("q"), 100)
	otype = args.get("type")

	###################################################################################################

	vals = list(product(*[S, K, IV, T, r, q]))
	n_options = len(vals)

	vals = np.repeat(vals, repeats=n_variables * len(increments), axis=0)
	delta = np.tile(np.kron(np.eye(n_variables), increments), (n_options, 1))
	vals = vals * (1 + delta)

	options = pd.DataFrame(vals, columns = columns)
	options['option_type'] = otype

	###################################################################################################

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

	options.loc[:, greek_columns] = options[greek_columns].replace([-np.inf, np.inf], np.nan)
	options.loc[:, greek_columns] = options[greek_columns].round(6).fillna(0)
	options.columns = display_columns

	###################################################################################################

	idc = [
		n_increments + i * (n_variables * len(increments)) - 1
		for i in range(n_options) 
	]

	table = options.iloc[idc, :].reset_index(drop=True)
	table['Time To Expiry'] = (table['Time To Expiry'] * 365).astype(int)

	c = ["Implied Volatility", "Rate", "Dividend Yield"]
	table.loc[:, c] = table.loc[:, c] * 100

	table = table.to_html(classes=["table table-sm table-hover table-borderless"])

	return {
		"table" : table,
		"options" : options.values.tolist(),
		"n_options" : n_options,
		"n_increments" : len(increments),
		"names" : list(options.columns)
	}