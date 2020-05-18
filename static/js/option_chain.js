
var stockPrice = 272.2;
var stockPriceIdx = 11;
var multiplier = 1;

function onChangeMoneyness(){

	let ele = document.getElementById("moneyness");
	let value = ele.value;

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = "0.2";
	}

	let pointCtr = value.split(".").length - 1
	let pctCtr = value.split("%").length - 1

	if ((pointCtr > 1) || (pctCtr > 1)) {
		value = "0.2";
	}

	factor = 1;
	if (value.indexOf("%") == value.length - 1) {
		factor /= 100;
	}

	value = parseFloat(value) * factor;
	ele.value = (value * 100).toFixed(2) + "%"

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

	let ele = document.getElementById("multiplier");
	let value = ele.value;

	if ((value == "") | (value.indexOf("-") != -1)) {
		value = "1";
	}

	value = parseInt(value);
	if (isNaN(value)) {
		value = 1
	}

	multiplier = value;
	ele.value = value;

}

function onWheelClickScroll(i, id){

	$('#optionChainAccordion').on('shown.bs.collapse', function() {
  		
		let bottomRow = document.getElementById("bottomRow");
		let header = document.getElementById(id);
		bottomRow.scroll(0, i * header.offsetHeight);

	})

}