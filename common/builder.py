from common.const import COLS, COLS_FMT, PARSER
from common.utils.html import html
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

class Builder:

	def __init__(self, option_chain):

		self.stock_price = 316.73

		self.option_chain = option_chain
		self._option_chain = ""

		self.option_data = self.option_chain.set_index("option_id")
		self.option_data = self.option_data.T.to_dict()

		self.generate_option_chain()

	def generate_option_chain(self):

		def format_wheel(expiration):

			exp = self.option_chain.expiration_date == expiration
			exp = self.option_chain[exp]
		
			calls = exp[exp.option_type == "C"]
			calls = calls[COLS]
			
			puts = exp[exp.option_type == "P"]
			puts = puts[COLS[::-1]]
			
			wheel = calls.merge(puts, on="strike_price", how="outer")
			wheel = wheel.fillna("-")
			wheel = wheel.sort_values("strike_price")
			wheel = wheel.reset_index(drop=True)

			call_ids = list(wheel.option_id_x)
			put_ids = list(wheel.option_id_y)

			wheel = wheel.drop(["option_id_x", "option_id_y"], axis=1)

			line = [''] * wheel.shape[1]
			line[int(len(line) / 2)] = self.stock_price
			line = pd.DataFrame([line], columns = wheel.columns)

			idx = wheel[wheel.strike_price <= self.stock_price]
			idx = idx.index.values[-1]

			wheel = pd.concat([
				wheel.iloc[:idx],
				line,
				wheel.iloc[idx:]
			])
			wheel.columns = COLS_FMT

			_wheel = wheel.to_html(index=False, classes="table table-hover",
								   header=True, border=0)
			_wheel = BeautifulSoup(_wheel, PARSER)

			###########################################################################################

			tds = _wheel.find_all("td")
			
			call_bids = tds[2::23]
			call_asks = tds[4::23]

			put_bids = tds[20::23]
			put_asks = tds[18::23]

			values = zip(call_bids, call_asks, put_bids, put_asks, call_ids, put_ids)
			for i, (cb, ca, pb, pa, call_id, put_id) in enumerate(values):

				if i == idx:
					continue

				if cb.text != "-":

					cb["class"] = "sellOrder"
					cb["onclick"] = f'addToPosition(-1, "{call_id}")'

					ca["class"] = "buyOrder"
					ca["onclick"] = f'addToPosition(1, "{call_id}")'

				if pb.text != "-":

					pb["class"] = "sellOrder"
					pb["onclick"] = f'addToPosition(-1, "{put_id}")'

					pa["class"] = "buyOrder"
					pa["onclick"] = f'addToPosition(1, "{put_id}")'

			ths = _wheel.find_all("th", text="Rho")

			ths[0].insert(0, _wheel.new_tag("br"))
			ths[0].insert(0, "Calls")

			ths[1].insert(0, _wheel.new_tag("br"))
			ths[1].insert(0, "Puts")

			stock_row = _wheel.find_all("tr")[idx+1]
			stock_row['class'] = "stockRow"

			###########################################################################################

			return str(_wheel)

		expirations = self.option_chain.groupby("expiration_date").apply(
			lambda x: int(x.time_to_expiry.unique() * 252)
		)

		collapsed = ""
		show = " show"
		aria_expanded = "true"

		for i, (expiration, days) in enumerate(expirations.items()):

			_expiration = expiration.replace("-", "")

			header_button = html("button", f"{expiration} - {days} Days", {
				"class" : f"btn btn-link btn-small{collapsed} chainButton",
				"type" : "button",
				"data-toggle" : "collapse",
				"data-target" : f"#collapse{_expiration}",
				"aria-expanded" : aria_expanded,
				"aria-controls" : f"collapse{_expiration}",
				"onclick" : f'onWheelClickScroll("{i}","heading{_expiration}")'
			})
			header = html("h6", header_button, {"class" : "m-0 wheelTab"})
			card_header = html("div", header, {
				"class" : "card-header",
				"id" : f"heading{_expiration}"
			})

			card_body = html("div", format_wheel(expiration), {"class" : "card-body wheelCardBody"})
			card_body = html("div", card_body, {
				"id" : f"collapse{_expiration}",
				"class" : f"collapse{show}",
				"aria-labelledby" : f"heading{_expiration}",
				"data-parent" : "#optionChainAccordion"
			})

			collapsed = " collapsed"
			show = ""
			aria_expanded = "false"

			self._option_chain += html("div", card_header+card_body, {"class" : "card bg-dark"})