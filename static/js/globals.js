
var options = null;
var position = null;
var riskGraph = null;
var position_info = null;

var stockPriceIdx = 11;
var stockPrice = null;
var priceIncrement = null;

var moneynessVals = {
	"default" : 0.4,
	"current" : 0.4
}
var multiplierVals = {
	"default" : 1,
	"current" : 1
}
var uChangeVals = {
	"default" : 100,
	"current" : 100
}

function initGlobals(_options, _position_info, _stock_info){

	var moneyness = document.getElementById("moneyness");
	var multiplier = document.getElementById("multiplier");
	var uChange = document.getElementById("uChange");
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
				backgroundColor: 'rgba(52, 58, 64, 0.15)',
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
				titleAlign:'center',
				titleFontStyle:'bold',
				bodyAlign:'center',
				bodyFontStyle:'bold',
				callbacks: {
					title: function(tooltipItem, data) {
                    	return "Price: "+tooltipItem[0].label;
                	}
				}
			},

			elements: {
				
				point: {
					radius:0,
					hitRadius:20,
					hoverRadius:2,
					pointStyle:'circle'
				},

			},

			scales: {

				xAxes: [{
					
					type: 'linear',
					position: 'bottom',

					scaleLabel: {
						display: false,
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
						display: false,
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