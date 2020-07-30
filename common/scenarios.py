from common.utils.html import html
import pandas as pd

###################################################################################################

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

scenarios_htmls = {
	"option_tr" : option_tr,
	"accordion_tr" : accordion_tr,
	"accordion" : accordion
}