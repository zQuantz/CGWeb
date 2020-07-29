from common.utils.html import html

_input = html("input", "", {
	"type" : "tel",
	"class" : "quantityInput",
	"onchange" : "editQuantity(this)",
	"pattern" : "[-]?[1-9][0-9]*",
	"required" : "required"
})

tr = html("td", html("a", "X", {"href" : "#", "onclick" : 'removePosition(this)'}))	
tr += html("td", "OPTION_ID")
tr += html("td", _input)
tr = html("tr", tr, {"id" : "OPTION_ID"})