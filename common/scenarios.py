from common.utils.html import html

tr = html("td", html("a", "X", {"href" : "#", "onclick" : 'removePosition(this)'}))
tr += html("td", "OPTION_ID")
tr += html("td", html("input", "", {"type" : "text", "class" : "quantityInput", "onchange" : "editQuantity(this)"}))
tr = html("tr", tr, {"id" : "OPTION_ID"})