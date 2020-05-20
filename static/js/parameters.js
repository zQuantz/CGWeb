
function onChangeMoneyness(){

	let value = moneyness.value;

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = dMoneyness;
	}

	let pointCtr = value.split(".").length - 1
	let pctCtr = value.split("%").length - 1

	if ((pointCtr > 1) || (pctCtr > 1)) {
		value = dMoneyness;
	}

	factor = 1;
	if (value.indexOf("%") == value.length - 1) {
		factor /= 100;
	}

	value = parseFloat(value) * factor;
	moneyness.value = (value * 100).toFixed(2) + "%"

	let rows = $(".dataframe tbody tr");
	rows.removeAttr("hidden");

	rows.get().forEach(row => {
		let price = parseFloat(row.children[stockPriceIdx].textContent);
		if (Math.abs( (price / stockPrice) - 1) > value){
			row.setAttribute("hidden", true);
		}
	})
}

function onChangeMultiplier() {

	let value = multiplier.value;

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = vMultiplier;
	}

	value = parseInt(value);
	if (isNaN(value)) {
		value = vMultiplier;
	}

	vMultiplier = value;
	multiplier.value = value;

}

function onWheelClickScroll(i, id){

	$('#optionChainAccordion').on('shown.bs.collapse', function() {
		let header = document.getElementById(id);
		bottomRow.scroll(0, i * header.offsetHeight);
	})
}