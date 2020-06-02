
function parseUserFloat(element, values){

	let value = element.value;
	let factor = 1;

	let pointCtr = value.split(".").length - 1
	let pctCtr = value.split("%").length - 1

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = values.default;
	}
	else if ((pointCtr > 1) || (pctCtr > 1)) {
		value = values.default;
	}
	else if (value.indexOf("%") == value.length - 1) {
		factor /= 100;
	}

	return {
		value:value,
		factor:factor
	}

}

function onChangeMoneyness(){

	values = parseUserFloat(moneyness, moneynessVals)
	
	value = values.value;
	factor = values.factor;

	moneynessVals.current = parseFloat(value) * factor;
	moneyness.value = (moneynessVals.current * 100).toFixed(0) + "%"

	let rows = $(".dataframe tbody tr");
	rows.removeAttr("hidden");

	rows.get().forEach(row => {
		let price = parseFloat(row.children[stockPriceIdx].textContent);
		if (Math.abs( (price / stockPrice) - 1) > moneynessVals.current){
			row.setAttribute("hidden", true);
		}
	})
}

function onChangeUChange(){

	values = parseUserFloat(uChange, uChangeVals)
	
	value = values.value;
	factor = values.factor;

	uChangeVals.current = Math.round(parseFloat(value) * factor * 100);
	uChange.value = uChangeVals.current + "%";

	displayRiskGraph();

}

function onChangeMultiplier() {

	let value = multiplier.value;

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = multiplierVals.default;
	}

	value = parseInt(value);
	if (isNaN(value)) {
		value = multiplierVals.default;
	}

	multiplierVals.current = value;
	multiplier.value = value;

}

function onWheelClickScroll(i, id){

	$('#optionChainAccordion').on('shown.bs.collapse', function() {
		let header = document.getElementById(id);
		bottomRow.scroll(0, i * header.offsetHeight);
	})
}