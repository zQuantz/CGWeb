from common.greeks import calculate_greeks
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
	"days_to_expiry",
	"volume",
	"open_interest",
	"stock_price",
	"option_price",
	"implied_volatility",
	"quantity",
	"cost",
	"delta",
	"gamma",
	"theta",
	"vega",
	"last_stock",
	"last_price",
	"last_vol",
	"last_cost",
	"pnl"
]

display_cols = [
	"Execution Date",
	"Days to Expiry",
	"Volume",
	"Open Interest",
	"Stock Price",
	"Option Price",
	"IV",
	"Quantity",
	"Cost",
	"Delta",
	"Gamma",
	"Theta",
	"Vega",
	"Last Stock Price",
	"Last Option Price",
	"Last IV",
	"Last Cost",
	"Profit/Loss"
]

###################################################################################################

class Scenarios:

	def __init__(self, connector):

		self.reset()
		self._option_ids = None

		self.connector = connector
		self.generate_html_templates()

	def reset(self):

		self.ticker = None
		self.symbol = None
		self.selectors = None
		self._position_rows = None
		self.position_attributions = None

	def generate_option_ids(self, tickers):

		if not tickers:
			self.reset()
			return

		self.ticker = tickers[0]
		self.symbol = {
			"symbol" : f"{self.connector.ticker_info[self.ticker]['exchange_code']}:{self.ticker}",
			"ticker" : self.ticker
		}

		option_ids = self.connector.get_option_ids(tuple(tickers))
		oids = option_ids.option_id.str.split(" ", expand=True)
		oids.columns = ['ticker', 'expiration', 'tstrike']

		def convert(ticker):
			ticker = ticker.groupby("expiration")["tstrike"].apply(list)
			return ticker.to_dict()

		selectors = oids.groupby("ticker").apply(convert).to_dict()

		tickers = "".join([
			html("option", ticker, {"value" : ticker})
			for ticker in selectors
		])

		expirations = {
			ticker : "".join([
				html("option", expiration, {"value" : expiration})
				for expiration in selectors[ticker]
			])
			for ticker in selectors
		}

		tstrikes = {
			ticker : {
				expiration : "".join([
					html("option", tstrike, {"value" : tstrike})
					for tstrike in selectors[ticker][expiration]
				])
				for expiration in selectors[ticker]
			}
			for ticker in selectors
		}

		self.selectors = {
			"tickers" : tickers,
			"expirations" : expirations,
			"tstrikes" : tstrikes
		}

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
				AND options.date_current
					BETWEEN "{dates[0]}" AND "{dates[1]}" 
				AND options.date_current >= "{dates[0]}"
				AND options.date_current <= "{dates[1]}"
			"""
			
			clauses.append(f"({clause})")

		clauses = " OR ".join(clauses)
		options = self.connector.get_scenarios(clauses)
		options = calculate_greeks(options)

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

			cumattrs = attrs.cumsum(axis=0)
			cumattrs.columns = cum_cols
			os = pd.concat([os, cumattrs], axis=1)

			os.loc[:, attr_cols] = attrs
			os.iloc[0, :] = os.iloc[0, :].fillna(0)
			
			os['attr'] = os.delta_attr + os.gamma_attr + os.speed_attr
			os['attr'] += os.vega_attr + os.vomma_attr + os.ultima_attr
			os['attr'] += os.rho_attr + os.theta_attr + os.vanna_attr
			os['attr'] += os.charm_attr + os.veta_attr + os.color_attr
			os['attr'] += os.zomma_attr
			
			os['cum_attr'] = os.attr.cumsum()
			
			return os

		###############################################################################################

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
			position['quantity'] = position.option_id.map(oid_dir_map)
			
			ccum_cols = cum_cols + ['cum_attr']
			position.loc[:, ccum_cols] = position.loc[:, ccum_cols].multiply(position.quantity, axis=0)
			position_pnl = position.groupby('date_current').sum().loc[:, ccum_cols]
			
			position_pnl = position_pnl.to_dict('list')
			position_pnl = {key[4:-5] : position_pnl[key] for key in position_pnl}
			position_pnl['net'] = position_pnl['']
			del position_pnl['']			

			attributions['position'] = position_pnl
			
			for oid in oids:
				
				option_pnl = position[position.option_id == oid]
				stock_price = option_pnl.stock_price.values.tolist()

				option_pnl = option_pnl.loc[:, ccum_cols]
				option_pnl = option_pnl.to_dict('list')
				
				option_pnl = {key[4:-5] : option_pnl[key] for key in option_pnl}
				option_pnl['net'] = option_pnl['']
				del option_pnl['']
				
				option_pnl['stock price'] = stock_price
				attributions[oid] = option_pnl

			###############################################################################################
			
			x = position.date_current.value_counts()
			x = x[x == len(oids)]
			pdetails = position[position.date_current.isin(x.index)]

			dates = pdetails.date_current.unique()
			dates = [datetime(d.year, d.month, d.day).timestamp() for d in dates]
			dates = [date * 1000 for date in dates]
			attributions['dates'] = dates
			
			pdetails_end = pdetails.iloc[-len(oids):].reset_index(drop=True)
			pdetails = pdetails.iloc[:len(oids)].reset_index(drop=True)
			
			single_ticker = pdetails.ticker.nunique() == 1
			pdetails = pdetails.drop(["ticker", "option_type", "strike_price", "bid_price", "ask_price"], axis=1)

			pdetails['implied_volatility'] = pdetails.implied_volatility
			pdetails['days_to_expiry'] = pdetails.days_to_expiry
			pdetails['cost'] = pdetails.option_price * pdetails.quantity

			pdetails['last_stock'] = pdetails_end.stock_price
			pdetails['last_price'] = pdetails_end.option_price
			pdetails['last_vol'] = pdetails_end.implied_volatility
			pdetails['last_cost'] = pdetails_end.option_price * pdetails_end.quantity

			pdetails['pnl'] = pdetails_end.option_price - pdetails.option_price 
			pdetails['pnl'] = (pdetails.pnl * pdetails.quantity).round(2)

			###############################################################################################

			net = [""] * len(display_cols)
			x = pdetails.iloc[:, 3:]

			sums = x.sum()
			psums = x.multiply(x.quantity, axis=0).sum()
			means = x.mean()

			net[8] = round(sums.cost, 2)
			net[16] = round(sums.last_cost, 2)
			net[17] = round(sums.pnl, 2)

			if single_ticker:

				net[6] = round(means.implied_volatility, 2)
				net[9] = round(psums.delta, 5)
				net[10] = round(psums.gamma, 5)
				net[11] = round(psums.theta, 5)
				net[12] = round(psums.vega, 5)
				net[15] = round(means.last_vol, 2)

				attributions['position']['stock price'] = attributions[oids[0]]['stock price']

			else:

				attributions['position']['stock price'] = []

			for i in [6, 15]:
				net[i] = str(net[i]) + "%"

			for i in [8, 16, 17]:
				net[i] = str(net[i]) + "$"

			###############################################################################################
			
			transpose_cols = pdetails.option_id.values
			pdetails = pdetails[ordered_cols]
			pdetails.columns = display_cols
			
			pdetails = pdetails.T
			pdetails.columns = transpose_cols
			
			###############################################################################################

			for label in ["IV", "Last IV"]:
				pdetails.loc[label, :] = pdetails.loc[label, :].astype(str) + "%"

			labels = ["Option Price", "Last Option Price", "Stock Price"]
			labels += ["Last Stock Price", "Cost", "Last Cost", "Profit/Loss"]
			for label in labels:
				pdetails.loc[label, :] = pdetails.loc[label, :].astype(str) + "$"

			pdetails['Net'] = net

			###############################################################################################

			idx = len(position_attributions)

			s2r1 = html("canvas", "", {"id" : f"PnLChart{idx}", "width" : 28, "height" : 18, "style" : "padding-top: 1rem;"})
			s2r1 = html("div", s2r1, {"class" : "col-lg-12", "style" : "padding-left: 0.25rem"})
			s2r1 = html("div", s2r1, {"class" : "row"})

			###############################################################################################

			instrumentOptions = html("option", "Position", {"value" : "position"})
			for option in oids:
				instrumentOptions += html("option", option, {"value" : option})

			s2r2r1 = html("select", instrumentOptions, {"class" : "selectpicker", "id" : f"instrumentSelect{idx}", "scenario" : idx})
			s2r2r1 = html("div", s2r2r1, {"class" : "col-8"})
			label = html("label", "Instrument", {"class" : "col-4 col-form-label"})
			s2r2r1 = html("div", label + s2r2r1, {"class" : "form-group row"})
			
			s2r2r2 = html("option", "Cummulative Change", {"value" : "c"})
			s2r2r2 += html("option", "Daily Change", {"value" : "d"})
			s2r2r2 = html("select", s2r2r2, {"class" : "selectpicker", "id" : f"representationSelect{idx}", "scenario" : idx})
			s2r2r2 = html("div", s2r2r2, {"class" : "col-8"})
			label = html("label", "Representation", {"class" : "col-4 col-form-label"})
			s2r2r2 = html("div", label + s2r2r2, {"class" : "form-group row", "style" : "margin-left: 2rem; border-left: 1px solid rgba(0, 0, 0, 0.25)"})

			s2r2 = html("div", s2r2r1 + s2r2r2, {"class" : "row", "style" : "margin-left: 1rem;"})

			###############################################################################################

			variableOptions = ""
			chart_options = ["Net", "Delta", "Gamma", "Theta", "Vega", "Rho", "Stock Price"]
			chart_options += ["Vanna", "Veta", "Speed", "Zomma", "Color", "Ultima", "Charm"]
			for option in chart_options:
				variableOptions += html("option", option, {"value" : option.lower()})

			s2r3r1 = html("select", variableOptions, {"class" : "selectpicker", "id" : f"variableSelectL{idx}", "multiple" : "multiple", "scenario" : idx})
			s2r3r1 = html("div", s2r3r1, {"class" : "col-8"})
			label = html("label", "L Variable(s)", {"class" : "col-4 col-form-label"})
			s2r3r1 = html("div", label + s2r3r1, {"class" : "form-group row"})

			s2r3r2 = html("select", variableOptions, {"class" : "selectpicker", "id" : f"variableSelectR{idx}", "multiple" : "multiple", "scenario" : idx})
			s2r3r2 = html("div", s2r3r2, {"class" : "col-8"})
			label = html("label", "R Variable(s)", {"class" : "col-4 col-form-label"})
			s2r3r2 = html("div", label + s2r3r2, {"class" : "form-group row", "style" : "margin-left: 1.175rem; border-left: 1px solid rgba(0, 0, 0, 0.25)"})

			s2r3 = html("div", s2r3r1 + s2r3r2, {"class" : "row", "style" : "margin-left: 1rem;"})

			###############################################################################################

			s2 = html("div", s2r1 + s2r2 + s2r3, {"class" : "col-lg-6 positionSegment", "style" : "margin-right: none;"})

			###############################################################################################

			s1 = html("h3", f"Scenario #{idx + 1}") + html("br", "") + html("h6", "Position Details")
			s1 += pdetails.to_html(classes="table table-sm table-hover smallTable", border=0, justify="unset")
			s1 = html("div", s1, {"class" : "col-lg-6 positionSegment"})

			position_rows.append(html("div", s1+s2, {"class" : "row positionRow"}))

			###############################################################################################

			for instrument in attributions:

				if instrument == "dates":
					continue

				variables = attributions[instrument]
				_variables = variables.copy()

				for key in _variables:
					_variables[key] = [0] + np.diff(_variables[key]).tolist()

				attributions[instrument] = {
					"c" : variables,
					"d" : _variables
				}

			position_attributions.append(attributions)

		self._position_rows = " ".join(position_rows)
		self.position_attributions = position_attributions

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