var positionAccordion = null;
var actionEntryTbody = null;
var startDateInput = null;
var optionSelect = null;
var endDateInput = null;

var accordion_tr = null;
var accordion = null;
var option_tr = null;

var positions = [];
var position = {};
var tickers = {};
var strikes = {};

var minDate = "2019-12-01";

function init(scenarios_htmls){

	actionEntryTbody = $("#actionEntryTbody");
	positionAccordion = $("#positionAccordion");

	optionSelect = $("#optionSelect");
	optionSelect.change(editPosition);

	accordion_tr = scenarios_htmls['accordion_tr'];
	accordion = scenarios_htmls['accordion'];
	option_tr = scenarios_htmls['option_tr'];

	startDateInput = $("#startDateInput");
	endDateInput = $("#endDateInput");

	let date = new Date().toISOString().split("T")[0]
	startDateInput.attr("max", date);
	startDateInput.attr("max", date);

	startDateInput.change(function() {
		endDateInput.attr("min", startDateInput.val())
	});

}

function removeOption(e){

	let id = e.parentElement.parentElement.id;
	delete position[id];

	optionSelect.selectpicker("val", Object.keys(position));
	optionSelect.selectpicker('refresh');

	editPosition();

}

function editQuantity(e) {

	let id = e.parentElement.parentElement.id;
	position[id] = e.value;
	editPosition();

}

function editPosition(){

	let newPosition = {};
	let newTickers = {};
	let newStrikes = {};

	actionEntryTbody.empty();

	options = optionSelect.val();
	options.forEach( (option, ctr) => {

		newPosition[option] = 0;

		let ntr = option_tr.replace("OPTION_ID", option);
		ntr = ntr.replace("OPTION_ID", option);

		actionEntryTbody.append(ntr);

		if(option in position){
			newPosition[option] = position[option];
		}

		$("#actionEntryTbody input:last").val(newPosition[option]);

		newTickers[option.split(" ")[0]] = 0;
		newStrikes[option.split(" ")[2].substring(1)] = 0;

	})

	position = newPosition;
	tickers = newTickers;
	strikes = newStrikes;

}

function resetPosition() {

	position = {};
	tickers = {};
	
	optionSelect.selectpicker("val", []);
	optionSelect.selectpicker("refresh");

	startDateInput.val("");
	endDateInput.val("");
	endDateInput.attr("min", minDate);

	editPosition();

}

function addPosition() {

	positions.push({
		position: position,
		startDate: startDateInput.val(),
		endDate: endDateInput.val(),
		tickers: Object.keys(tickers),
		strikes: Object.keys(strikes)
	})

	editPositions();

}

function editPositions() {

	positionAccordion.empty();
	positions.forEach( (pos, ctr) => {

		let label = `Dates: ${pos.startDate.replace("-", "/").replace("-", "/")} - `
		label += `${pos.endDate.replace("-", "/").replace("-", "/")}. `
		label += `Tickers: ${pos.tickers.sort().join(",")}. `
		label += `Strikes: ${pos.strikes.sort().join(",")}.`

		let acc = accordion.replace("CARD_HEADER_LABEL", label);
		for(let i = 0; i < 8; i++)
			acc = acc.replace("POSNUM", ctr);

		positionAccordion.append(acc);

		let table = $("#positionAccordion tbody:last");
		Object.entries(pos.position).forEach( entry => {
			acc_tr = accordion_tr.replace("OPTION_ID", entry[0]);
			acc_tr = acc_tr.replace("QUANTITY", entry[1]);
			table.append(acc_tr);
		})

	})

}

function removePosition(ctr){

	positions.splice(ctr, 1);
	editPositions();

}

function removeAllPositions(){
	
	positions = [];
	editPositions();

}

function analyzePositions(){

	let positions = [

		{
			startDate:  "2020-08-01",
			endDate: "2020-08-04",
			position: {
				"AAPL 2020-08-21 P400.0": "1",
				"AAPL 2020-08-21 C400.0": "-2"
			},
			strikes:["400.0"],
			tickers:["AAPL"]
		},
		{
			startDate:  "2020-08-01",
			endDate: "2020-08-04",
			position: {
				"AAPL 2020-08-21 P410.0": "-1",
				"AAPL 2020-08-21 C420.0": "-2"
			},
			strikes:["410.0","420.0"],
			tickers:["AAPL"]
		},

	]

	if (positions.length == 0)
		return;

	var request = new XMLHttpRequest();
	request.open("POST", "/scenarios/analyze");
	request.send(JSON.stringify(positions));

}