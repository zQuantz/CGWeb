from common.utils.html import html

class Builder:

	def __init__(self, data):

		self.data = data
		self._option_chain = ""

		self.generate_option_chain()

	def generate_option_chain(self):

		expirations = self.data.expiration_date.unique()

		collapsed = ""
		show = " show"
		aria_expanded = "true"

		for expiration in expirations:

			_expiration = expiration.replace("-", "")

			header_button = html("button", expiration, {
				"class" : f"btn btn-link btn-small{collapsed}",
				"type" : "button",
				"data-toggle" : "collapse",
				"data-target" : f"#collapse{_expiration}",
				"aria-expanded" : aria_expanded,
				"aria-controls" : f"collapse{_expiration}"
			})
			header = html("h6", header_button, {"class" : "m-0 wheelTab"})
			card_header = html("div", header, {
				"class" : "card-header",
				"id" : f"heading{_expiration}"
			})

			card_body = html("div", ".", {"class" : "card-body wheelCardBody"})
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