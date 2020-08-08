from common.utils.html import html
from datetime import datetime
from scipy.stats import norm
import sqlalchemy as sql
import pandas as pd
import numpy as np

###################################################################################################

cols = ['delta', 'gamma', 'speed', 'vega', 'vomma', 'ultima',
		'rho', 'theta', 'vanna', 'charm', 'veta', 'color', 'zomma']
attr_cols = [col+'_attr' for col in cols]
cum_cols = ["cum_"+col for col in attr_cols]

ordered_cols = [
	"date_current",
	"stock_price",
	"quantity",
	"option_price",
	"implied_volatility",
	"time_to_expiry",
	"volume",
	"open_interest",
	"delta",
	"gamma",
	"theta",
	"vega",
	"cost",
	"last_price",
	"pnl"
]
display_cols = [
	"Execution Date",
	"Stock Price",
	"Quantity",
	"Option Price",
	"IV",
	"Days to Expiry",
	"Volume",
	"Open Interest",
	"Delta",
	"Gamma",
	"Theta",
	"Vega",
	"Cost",
	"Last Option Price",
	"Profit/Loss"
]

greek_cols = [
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

###################################################################################################

class Scenarios:

	def __init__(self, connector):

		self._option_ids = None
		self._position_rows = None
		self.position_attributions = None

		self.connector = connector
		self.generate_html_templates()

	def generate_scenarios(self, data):

		positions, clauses = [], []
		for position in data:

			positions.append([
				tuple(position['position'].keys()),
				(position['startDate'], position['endDate']),
				tuple(map(int, position['position'].values()))
			])

			oids, dates, _ = positions[-1]

			if len(oids) > 1:
				clause = f"""
					option_id in {str(oids)}
				"""
			else:
				clause = f"""
					option_id = "{oids[0]}"
				"""
				
			clause += f"""
				AND options.date_current >= "{dates[0]}"
				AND options.date_current <= "{dates[1]}"
			"""
			
			clauses.append(f"({clause})")

		clauses = " OR ".join(clauses)
		options = self.connector.get_scenarios(clauses)

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

		###################################################################################################

		options.loc[:, greek_cols] = options[greek_cols].replace([-np.inf, np.inf], np.nan)
		options.loc[:, greek_cols] = options[greek_cols].round(6).fillna(0)
		options = options.sort_values(["date_current", "option_type"], ascending=True)

		def calculate_pnl_attribution(os):
		
			dt = os.date_current.diff().dt.days
			dt = dt.fillna(0)
			dt = 1
			
			dS = os.stock_price.diff().fillna(0).values
			dSig = os.implied_volatility.diff().fillna(0).values
			dSig *= 100
			dR = os.rate.diff().fillna(0).values * 100
			dOption = os.option_price.diff().fillna(0).values
			
			rho = os.rho.shift()
			delta = os.delta.shift()
			gamma = os.gamma.shift()
			speed = os.speed.shift()

			vega = os.vega.shift()
			vomma = os.vomma.shift()
			ultima = os.ultima.shift()

			vanna = os.vanna.shift()
			zomma = os.zomma.shift()

			theta = os.theta.shift()
			charm = os.charm.shift()
			veta = os.veta.shift()
			color = os.color.shift()
			
			os['delta_attr'] = dS * delta
			os['gamma_attr'] = 0.5 * dS * dS * gamma
			os['speed_attr'] = (1/6) * dS * dS * dS * speed
			
			os['vega_attr'] = dSig * vega
			os['vomma_attr'] = 0.5 * dSig * dSig * vomma * 0.01
			os['ultima_attr'] = (1/6) * dSig * dSig * dSig * ultima * 0.01 * 0.01

			os['net_delta_attr'] = os.delta_attr + os.gamma_attr + os.speed_attr
			os['net_vega_attr'] = os.vega_attr + os.vomma_attr + os.ultima_attr
			
			os['rho_attr'] = dR * rho
			os['theta_attr'] = theta * dt

			os['vanna_attr'] = dS * dSig * vanna * 0.01
			os['charm_attr'] = dS * dt * charm
			os['veta_attr'] = dSig * dt * veta * 0.01
			os['color_attr'] = 0.5 * dS * dS * dt * color
			os['zomma_attr'] = 0.5 * dS * dS * dSig * zomma * 0.01
			
			os['attr'] = os.delta_attr + os.gamma_attr + os.speed_attr
			os['attr'] += os.vega_attr + os.vomma_attr + os.ultima_attr
			os['attr'] += os.rho_attr + os.theta_attr + os.vanna_attr
			os['attr'] += os.charm_attr + os.veta_attr + os.color_attr
			os['attr'] += os.zomma_attr
			
			scale = os.option_price.diff() / os.attr    
			attrs = os.loc[:, attr_cols]
			attrs = attrs.div(os.option_price.shift(), axis=0)
			attrs = attrs.multiply(scale, axis=0)
			attrs = attrs.multiply(os.option_price.shift(), axis=0)    
			os.loc[:, attr_cols] = attrs

			cumattrs = attrs.cumsum(axis=0)
			cumattrs.columns = cum_cols
			os = pd.concat([os, cumattrs], axis=1)
			
			os['attr'] = os.delta_attr + os.gamma_attr + os.speed_attr
			os['attr'] += os.vega_attr + os.vomma_attr + os.ultima_attr
			os['attr'] += os.rho_attr + os.theta_attr + os.vanna_attr
			os['attr'] += os.charm_attr + os.veta_attr + os.color_attr
			os['attr'] += os.zomma_attr
			
			os['cum_attr'] = os.attr.cumsum()
			
			os['approximated_price'] = os.option_price.shift() + os.attr
			
			return os

		position_attributions, position_rows = [], []

		for position in positions:
			
			attributions = {}
			
			oids, dates, dirs = position
			oid_dir_map = {oid : dir_ for oid, dir_ in zip(oids, dirs)}

			position = options[options.option_id.isin(oids)]
			position = position[position.date_current >= datetime.strptime(dates[0], "%Y-%m-%d").date()]
			position = position[position.date_current <= datetime.strptime(dates[1], "%Y-%m-%d").date()]
			
			x = position.date_current.value_counts()
			x = x[x == len(oids)]
			position = position[position.date_current.isin(x.index)]

			position = pd.concat([
				calculate_pnl_attribution(position.iloc[i::len(oids), :].copy())
				for i in range(len(oids))
			], axis=0)
			position = position.sort_values(["date_current", "option_id"])
			position['direction'] = position.option_id.map(oid_dir_map)
			
			ccum_cols = cum_cols + ['cum_attr']
			position.loc[:, ccum_cols] = position.loc[:, ccum_cols].multiply(position.direction, axis=0)
			position_pnl = position.groupby('date_current').sum().loc[:, ccum_cols][1:]
			
			position_pnl = position_pnl.to_dict('list')
			position_pnl = {key[4:-5] : position_pnl[key] for key in position_pnl}
			position_pnl['net'] = position_pnl['']
			del position_pnl['']
			
			attributions['position'] = position_pnl
			
			for oid in oids:
				
				option_pnl = position[position.option_id == oid].loc[:, ccum_cols][1:]
				option_pnl = option_pnl.to_dict('list')
				
				option_pnl = {key[4:-5] : option_pnl[key] for key in option_pnl}
				option_pnl['net'] = option_pnl['']
				del option_pnl['']
				
				attributions[oid] = option_pnl
				
			position_attributions.append(attributions)
			
			###############################################################################################
			
			x = position.date_current.value_counts()
			x = x[x == len(oids)]
			pdetails = position[position.date_current.isin(x.index)]
			
			pdetails_end = pdetails.iloc[-len(oids):].reset_index(drop=True)
			pdetails = pdetails.iloc[:len(oids)].reset_index(drop=True)
			
			pdetails['last_price'] = pdetails_end.option_price

			pdetails['pnl'] = pdetails_end.option_price - pdetails.option_price 
			pdetails['pnl'] = pdetails.pnl * pdetails.direction
			
			single_ticker = pdetails.ticker.nunique() == 1
			pdetails = pdetails.drop(["ticker", "option_type", "strike_price", "bid", "ask"], axis=1)

			pdetails['implied_volatility'] = pdetails.implied_volatility * 100
			pdetails['time_to_expiry'] = np.round(pdetails.time_to_expiry * 365)

			pdetails['quantity'] = pdetails.option_id.map(oid_dir_map)
			pdetails['cost'] = pdetails.option_price * pdetails.quantity

			###############################################################################################

			net = [""] * len(display_cols)

			if single_ticker:
				x = pdetails[['delta', 'gamma', 'theta', 'vega', 'option_price']]
				x = x.multiply(pdetails.quantity, axis=0).sum().round(6)
				net[-6:-1] = x.values.tolist()
			else:
				net[-2] = (pdetails.option_price * pdetails.quantity).sum()
				
			net[-1] = pdetails.pnl.sum().round(2)

			###############################################################################################
			
			c = ["pnl", "implied_volatility", "stock_price", "last_price"]
			pdetails.loc[:, c] = pdetails.loc[:, c].round(2)
			
			transpose_cols = pdetails.option_id.values
			pdetails = pdetails[ordered_cols]
			pdetails.columns = display_cols
			
			pdetails = pdetails.T
			pdetails.columns = transpose_cols
			
			###############################################################################################
			
			pdetails.loc["IV", :] = pdetails.loc["IV", :].astype(str) + "%"
			pdetails.loc["Option Price", :] = pdetails.loc["Option Price", :].astype(str) + "$"
			pdetails.loc["Stock Price", :] = pdetails.loc["Stock Price", :].astype(str) + "$"

			pdetails['Net'] = net
			pdetails.loc["Last Option Price", :] = pdetails.loc["Last Option Price", :].astype(str) + "$"
			pdetails.loc["Cost", :] = pdetails.loc["Cost", :].astype(str) + "$"
			pdetails.loc["Profit/Loss", :] = pdetails.loc["Profit/Loss", :].astype(str) + "$"

			###############################################################################################

			idx = len(position_attributions)

			s3r1 = html("canvas", "", {"id" : f"PnLChart{idx}", "width" : 3, "height" : 2, "style" : "padding-top: 1rem;"})
			s3r1 = html("div", s3r1, {"class" : "col-lg-12", "style" : "padding-left: 0.25rem"})
			s3r1 = html("div", s3r1, {"class" : "row"})

			s3r2 = ""
			chart_options = ["Net", "Delta", "Gamma", "Theta", "Vega", "Rho", "Vanna"]
			chart_options += ["Veta", "Speed", "Zomma", "Color", "Ultima", "Charm"]
			for option in chart_options:
				s3r2 += html("option", option, {"value" : option.lower()}) 

			s3r2 = html("select", s3r2, {"class" : "selectpicker", "id" : f"variableSelect{idx}", "multiple" : "multiple"})
			s3r2 = html("div", s3r2, {"class" : "col-lg-12"})
			s3r2 = html("div", s3r2, {"class" : "row"})

			s3 = html("div", s3r1 + s3r2, {"class" : "col-lg-4 positionSegment", "style" : "margin-right: none;"})

			###############################################################################################

			s2 = html("div", "", {"class" : "col-lg-3 positionSegment"})

			###############################################################################################

			s1 = html("h3", f"Scenario #{idx}") + html("br", "") + html("h6", "Position Details")
			s1 += pdetails.to_html(classes="table table-sm table-hover smallTable", border=0, justify="unset")
			s1 = html("div", s1, {"class" : "col-lg-5 positionSegment"})

			###############################################################################################

			position_rows.append(html("div", s1+s2+s3, {"class" : "row positionRow"}))

		self._position_rows = " ".join(position_rows)
		self.position_attributions = position_attributions

	def generate_option_ids(self, tickers):

		if not tickers:
			self.option_ids = None
			return

		option_ids = self.connector.get_option_ids(tuple(tickers))
		option_ids = option_ids.option_id.values

		self._option_ids = ""
		for option_id in option_ids:
			self._option_ids += html("option", option_id, {})

	def generate_html_templates(self):

		option_input = html("input", "", {
			"type" : "tel",
			"class" : "quantityInput",
			"onchange" : "editQuantity(this)",
			"pattern" : "[-]?[1-9][0-9]*",
			"required" : "required"
		})

		option_tr = html("td", html("a", "X", {"href" : "#", "onclick" : 'removeOption(this)'}))	
		option_tr += html("td", "OPTION_ID")
		option_tr += html("td", option_input)
		option_tr = html("tr", option_tr, {"id" : "OPTION_ID"})

		###################################################################################################

		accordion_header = html("button", "CARD_HEADER_LABEL", {
				"class" : "btn btn-link accordionButton",
				"type" : "button",
				"data-toggle" : "collapse",
				"data-target" : "#positionCardPOSNUM",
				"aria-expanded" : "false",
				"aria-controls" : "positionCardPOSNUM",
				"style" : "margin-left: -0.25rem"
			})
		accordion_header += html("button", "X", {
				"class" : "btn btn-link accordionButton cancelPositionButton", "onclick" :
				"removePosition(POSNUM)"
			})
		accordion_header = html("h2", accordion_header, {"class" : "mb-0 accordionTab"})
		accordion_header = html("div", accordion_header, {
				"class" : "card-header",
				"id" : "positionPOSNUMAccordionHeader"
			})

		accordion_body = """
		<table class="table table-sm table-hover">

			<thead>
				<tr>
					<th>Option</th>
					<th>Quantity</th>
				</tr>
			</thead>

			<tbody></tbody>

		</table>
		"""
		accordion_body = html("div", accordion_body, {"class" : "container-fluid", "style" : "margin-top: 0.5rem"})
		accordion_body = html("div", accordion_body, {"class" : "card-body accordionCardBody"})
		accordion_body = html("div", accordion_body, {
				"id" : "positionCardPOSNUM",
				"class" : "collapse",
				"aria-labelledby" : "positionPOSNUMAccordionHeader",
				"data-parent" : "#positionAccordion"
			})

		accordion = html("div", accordion_header + accordion_body, {
				"class" : "card bg-dark",
				"style" : "border-radius: 0px; border-bottom: 1px solid white"
			})

		accordion_tr = html("td", "OPTION_ID")
		accordion_tr += html("td", "QUANTITY")
		accordion_tr = html("tr", accordion_tr)

		###################################################################################################

		self.templates = {
			"option_tr" : option_tr,
			"accordion_tr" : accordion_tr,
			"accordion" : accordion
		}