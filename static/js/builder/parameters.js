
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
		bottomRow.style.overflowY = "hidden";
	})

	bottomRow.style.overflowY = "scroll";
}

function addTickerDates(){
	
	let ticker = document.getElementById("tickerSelect").value;
	if(ticker == ""){
		return;
	}

	let dateSelect = $("#tickerDateSelect");
	dateSelect.empty();

	dateSelect.append(unique_dates['LIVE']);
	ticker_dates[ticker].forEach(date => {
		dateSelect.append(unique_dates[date]);
	})

	dateSelect.selectpicker("refresh");

}

function resetExecuteModal(){

	$("#executeUsernameSelect").val("Joe").change();
	$("#executePasswordInput").val("").change();

	$("#executeDirectionSelect").val("None").change();
	$("#executeStrategySelect").val("None").change();

	$("#executeSentimentSelect").val("None").change();
	$("#executionTradeNotes").val("").change();

	$("#executeImageInput").val("").change();
	$("#executeImageLabel").val("").change();

	b64Images = "";
	imageFileNames = "";

	document.getElementById("executeImageLabel").textContent = "";

}

function resetExecuteModalBadge(){

	let classes = [
		"badge-success",
		"badge-danger",
		"badge-secondary"
	];
	modalStatusBadge.classList.remove(...classes);

	modalStatusBadge.classList.add("badge-secondary");
	modalStatusBadge.innerText = "Pending";
	
}

function readFileAsync(file) {
  return new Promise((resolve, reject) => {
    let fileReader = new FileReader();

    fileReader.onload = function(fileLoadedEvent) {
		resolve(fileLoadedEvent.target.result);
	};

    fileReader.onerror = reject;
    fileReader.readAsDataURL(file);

  })
}

async function encodeImagesAsB64() {

	let files = document.getElementById("executeImageInput").files;
	let label = "";

	for(let i = 0; i < files.length; i++){

		imageFileNames += files[i].name;
		label += files[i].name;
		b64Images += await readFileAsync(files[i]);

		if(i < files.length - 1){
			label += ",";
			imageFileNames += "/////";
			b64Images += "_____";
		}

	}

	document.getElementById("executeImageLabel").textContent = label;

}
