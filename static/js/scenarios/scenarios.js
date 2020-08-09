var positionAttributions = null;
var positionAccordion = null;
var actionEntryTbody = null;
var startDateInput = null;
var optionSelect = null;
var endDateInput = null;

var accordion_tr = null;
var accordion = null;
var option_tr = null;

var scenarioCharts = [];
var positions = [];
var position = {};
var tickers = {};
var strikes = {};

var minDate = "2019-12-01";
var colors = [
	'rgba(179,43,235)',
	'rgba(212,177,23)',
	'rgba(232,76,18)',
	'rgba(88,63,241)',
	'rgba(103,252,104)',
	'rgba(135,207,253)',
	'rgba(252,250,91)',
	'rgba(211,39,188)',
	'rgba(241,53,71)',
	'rgba(7,31,91)',
	'rgba(206,73,141)',
	'rgba(51,206,70)',
	'rgba(153,48,148)',
	'rgba(114,88,30)',
	'rgba(67,45,139)',
	'rgba(79,239,233)',
	'rgba(245,32,250)',
	'rgba(124,81,226)',
	'rgba(185,78,65)',
	'rgba(92,0,98)',
	'rgba(60,18,148)',
	'rgba(134,6,19)',
	'rgba(125,231,14)',
	'rgba(191,139,219)',
	'rgba(75,137,87)',
	'rgba(6,178,146)',
	'rgba(14,212,247)',
	'rgba(193,58,162)',
	'rgba(224,178,58)',
	'rgba(248,156,69)',
	'rgba(204,44,128)',
	'rgba(178,116,31)',
	'rgba(8,43,224)',
	'rgba(121,86,160)',
	'rgba(154,60,239)',
	'rgba(21,8,12)',
	'rgba(129,13,251)',
	'rgba(160,100,161)',
	'rgba(122,197,150)',
	'rgba(131,200,150)',
	'rgba(243,144,69)',
	'rgba(75,145,79)',
	'rgba(219,20,160)',
	'rgba(204,127,161)',
	'rgba(24,3,146)',
	'rgba(142,22,198)',
	'rgba(84,92,161)',
	'rgba(22,0,193)',
	'rgba(170,197,16)',
	'rgba(77,50,145)',
	'rgba(35,123,63)',
	'rgba(29,152,138)',
	'rgba(204,58,112)',
	'rgba(52,14,198)',
	'rgba(51,203,178)',
	'rgba(116,187,26)',
	'rgba(85,149,88)',
	'rgba(207,252,17)',
	'rgba(77,164,185)',
	'rgba(88,13,162)',
	'rgba(28,155,108)',
	'rgba(77,32,90)',
	'rgba(41,177,19)',
	'rgba(183,225,7)',
	'rgba(26,90,224)',
	'rgba(42,7,229)',
	'rgba(137,74,2)',
	'rgba(77,154,25)',
	'rgba(4,89,33)',
	'rgba(182,162,64)',
	'rgba(44,121,154)',
	'rgba(66,240,187)',
	'rgba(198,136,121)',
	'rgba(95,167,155)',
	'rgba(5,15,50)',
	'rgba(51,119,142)',
	'rgba(43,238,50)',
	'rgba(56,31,7)',
	'rgba(219,209,22)',
	'rgba(95,203,159)',
	'rgba(220,32,69)',
	'rgba(103,225,167)',
	'rgba(15,102,86)',
	'rgba(248,173,201)',
	'rgba(76,240,11)',
	'rgba(130,181,208)',
	'rgba(82,41,170)',
	'rgba(43,80,229)',
	'rgba(173,183,199)',
	'rgba(59,109,155)',
	'rgba(2,161,231)',
	'rgba(204,68,175)',
	'rgba(123,79,140)',
	'rgba(157,188,251)',
	'rgba(84,128,4)',
	'rgba(193,115,44)',
	'rgba(189,48,83)',
	'rgba(48,247,124)',
	'rgba(104,151,197)',
	'rgba(58,33,23)'
]

var chartConfig = {

	type: 'line',
	data: {
		datasets: []
	},
	options: {
		
		title: {
			display:true,
			text:"P&L Attribution",
			position:"top"
		},

		legend: {
			display:true
		},

		tooltips: {
			enabled:false,
			mode: "y",
			bodyFontStyle: 'bold',
			callbacks: {}
		},

		elements: {
			
			point: {
				enabled:false,
				radius:0,
				hitRadius:10,
				hoverRadius:0,
				pointStyle:'circle'
			},

		},

		scales: {

			xAxes: [{
				
				type: 'linear',
				position: 'bottom',

				scaleLabel: {
					display: true,
					labelString: '',
					fontStyle: "bold",
					fontSize: 14,
					padding: {
						bottom: 0,
						top: -5
					}
				},

				gridLines: {}

			}],

			yAxes: [{
				
				type: "linear",
				id: "leftAxis",
				position: "left",
				scaleLabel: {
					display: true,
					labelString: '',
					fontStyle: "bold",
					fontSize: 14,
					padding: {
						bottom: -5,
						top: 5
					}
				},

				gridLines: {}

			},
			{
				
				display: "auto",
				type: "linear",
				id: "rightAxis",
				position: "right",
				scaleLabel: {
					display: true,
					labelString: '',
					fontStyle: "bold",
					fontSize: 14,
					padding: {
						bottom: -5,
						top: 5
					}
				},

				gridLines: {}

			}]

		}
	}
}

///////////////////////////////////////////////////////////////////////////////////////////////////

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
		position: Object.assign({}, position),
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

function scenarioParameterChange(){

	let idx = this.getAttribute("scenario");
	idx = Number(idx);

	let chart = scenarioCharts[idx];
	chart.data.datasets = [];

	let leftVariables = $(`#variableSelectL${idx}`);
	let rightVariables = $(`#variableSelectR${idx}`);
	let representation = $(`#representationSelect${idx}`);
	let instrument = $(`#instrumentSelect${idx}`);

	let attributions = positionAttributions[idx][instrument.val()];
	attributions = attributions[representation.val()];

	leftVariables.val().forEach( (variable, ctr1) => {

		let data = [];
		attributions[variable].forEach( (value, ctr2) => {
			
			data.push({
				y: value,
				x: ctr2
			})

		})

		chart.data.datasets.push({
			label: variable.substring(0, 1).toUpperCase() + variable.substring(1) + " (L)",
			data: data,
			borderColor: colors[ctr1],
			lineTension: 0,
			yAxisID: 'leftAxis',
			fill: false
		})

	})

	rightVariables.val().forEach( (variable, ctr1) => {

		let data = [];
		attributions[variable].forEach( (value, ctr2) => {
			
			data.push({
				y: value,
				x: ctr2
			})

		})

		chart.data.datasets.push({
			label: variable.substring(0, 1).toUpperCase() + variable.substring(1) + " (R)",
			data: data,
			borderColor: colors[ctr1 + 50],
			lineTension: 0,
			yAxisID: 'rightAxis',
			fill: false
		})

	})

	chart.update();

}

function analyzePositions(){

	if (positions.length == 0)
		return;

	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {

		if(this.readyState == 4 && this.status == 200){
			
			$("#scenarioAccordionCard").collapse("hide");

			let data = JSON.parse(this.responseText);
			positionAttributions = data.position_attributions;
			$("#mainContainer").append(data.position_rows);

			for(let i = 0; i < positionAttributions.length; i++){
				var ctx = document.getElementById(`PnLChart${i}`).getContext('2d');
				scenarioCharts.push(new Chart(ctx, Object.assign({}, chartConfig)));	
			}

			for(let i = 0; i < positionAttributions.length; i++){
				$(`#variableSelectL${i}`).change(scenarioParameterChange);
				$(`#variableSelectR${i}`).change(scenarioParameterChange);
				$(`#representationSelect${i}`).change(scenarioParameterChange);
				$(`#instrumentSelect${i}`).change(scenarioParameterChange);

				$(`#variableSelectL${i}`).selectpicker("val", "net");
				$(`#variableSelectL${i}`).selectpicker("refresh");
				$(`#variableSelectL${i}`).change();
			}

		}

	}

	request.open("POST", "/scenarios");
	request.send(JSON.stringify(positions));

}

function initCandles(symbol) {

	$("#tickerSelect").val(symbol.ticker);
	$("#tickerSelect").selectpicker("refresh");

	new TradingView.widget(
		{
			"height" : "100%",
			"width" : "100%",
			"symbol": symbol.symbol,
			"interval": "D",
			"timezone": "Etc/UTC",
			"theme": "dark",
			"style": "1",
			"locale": "en",
			"toolbar_bg": "#f1f3f6",
			"enable_publishing": false,
			"allow_symbol_change": true,
			"studies": [],
			"container_id": "tradingviewDiv"
		}
	);

}

function removeAllScenarios() {

	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {

		if(this.readyState == 4 && this.status == 200){
			
			$("#scenarioAccordionCard").collapse("show");

			scenarioCharts = [];
			positions = [];
			position = {};
			tickers = {};
			strikes = {};
			positionAttributions = null;

			window.location.href = "/scenarios";

		}
	}	

	request.open("POST", "/scenarios");
	request.send(JSON.stringify({"reset" : true}));

}