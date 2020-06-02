
var options = null;
var position = null;
var riskGraph = null;
var position_info = null;

var stockPriceIdx = 11;
var stockPrice = null;
var priceIncrement = null;

var dMoneyness = "0.4";
var vMultiplier = 1;
var pRange = 100;

function initGlobals(_options, _position_info, _stock_info){

	var moneyness = document.getElementById("moneyness");
	var multiplier = document.getElementById("multiplier");
	var bottomRow = document.getElementById("bottomRow");

	position = new Position();
	position_info = _position_info;
	options = _options;

	stockPrice = _stock_info['stock_price'];
	priceIncrement = _stock_info['price_increment'];

	initChart();

}

function initChart(){

	var ctx = document.getElementById('riskGraph').getContext('2d');
	riskGraph = new Chart(ctx, {
		
		type: 'line',
		
		data: {
			datasets: [{
				label: 'Payoff',
				borderColor: 'rgba(35, 255, 23)',
				backgroundColor: 'rgba(52, 58, 64, 1)',
				data: []
			}]
		},
		options: {
			
			title: {
				display:true,
				text:"Risk Graph",
				position:"top"
			},

			legend: {
				display:false
			},

			tooltips: {
				enabled:true,
				displayColors:false,
				bodyAlign:'center'
			},

			elements: {
				
				point: {
					radius:2,
					hitRadius:10,
					hoverRadius:2,
					pointStyle:'circle'
				},

			},

			scales: {

				xAxes: [{
					
					type: 'linear',
					position: 'bottom',
					suggestedMin: 0,
					scaleLabel: {
						display: true,
						labelString: 'Price',
						fontSize: 14,
						padding: {
							bottom: 0,
							top: -5
						}
					},

					gridLines: {}

				}],

				yAxes: [{
					
					scaleLabel: {
						display: true,
						labelString: 'Payoff',
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

	});
}