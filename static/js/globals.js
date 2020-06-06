
var options = null;
var position = null;
var riskGraph = null;
var ticker_dates = null;
var unique_dates = null;
var position_info = null;

var stockPrice = null;
var stockPriceIdx = 11;
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
	"default" : 1,
	"current" : 1
}

function initGlobals(_options, _position_info, _stock_info, _unique_dates, _ticker_dates){

	var uChange = document.getElementById("uChange");
	var moneyness = document.getElementById("moneyness");
	var bottomRow = document.getElementById("bottomRow");
	var multiplier = document.getElementById("multiplier");

	options = _options;
	position = new Position();
	
	unique_dates = _unique_dates;
	ticker_dates = _ticker_dates;
	position_info = _position_info;

	stockPrice = _stock_info['stock_price'];
	priceIncrement = _stock_info['price_increment'];

	initChart();
	initCandles();
	registerEvents()

}

function registerEvents(){

	$("#tickerSelect").on('changed.bs.select', function(e) {
		addTickerDates();
	});

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

function initCandles() {

	new TradingView.widget(
		{
			"height" : Math.round(0.81 * window.innerHeight),
			"width" : Math.round(0.76 * window.innerWidth),
			"symbol": "NASDAQ:AAPL",
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