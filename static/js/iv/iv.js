var ivChart = null;

colors = [
	'rgb(23,255,241)',
	'rgba(23,220,255)',
	'rgba(23,150,255)',
	'rgba(19,69,255)',
	'rgba(130,19,255)',
	'rgba(75,0,159)'
]

function init(){

	let ctx = document.getElementById(`ivChart`).getContext('2d');
	ivChart = new Chart(ctx, {

		type: 'line',
		data: {
			datasets: []
		},
		options: {

			title: {
				display: true,
				text: "Implied Volatility Grouped by Time to Expiration",
				position: "top",
				fontSize: 16
			},

			legend: {
				display:true
			},

			tooltips: {
				enabled: true,
				mode: "index",
				intersect: false,
				bodyFontStyle: 'bold',
				callbacks: {
					title: function(item, obj){
						let i = item[0].label.lastIndexOf(", ");
						return item[0].label.substring(0, i);
					},
					label: function(item, data){

	                    var label = data.datasets[item.datasetIndex].label || '';

	                    if (label) {
	                        label += ': ';
	                    }

	                    label += Math.round(item.yLabel * 100) / 100;
	                    label += "%";
	                    return label;

					}
				}
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

					type: 'time',
					time: {
						unit: "week",
					},
					ticks: {
						source: "auto",
						autoSkip: true,
						autoSkipPadding: 75,
						maxRotation: 0,
						minRotation: 0,
						beginAtZero: false
					},
					distribution: "series",

				}],

				yAxes: [{

					type: "linear",
					id: "leftAxis",
					position: "left",
					scaleLabel: {
						display: true,
						labelString: "Implied Volatility (%)",
						fontStyle: "bold",
						fontSize: 16,
					}

				}]

			}
		}
	})
}

function initTicker(data, symbol) {

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

	ivChart.data.labels = data.dates;
	ivChart.data.datasets.push({
		label: 'Global',
		data: data['Global'],
		borderColor: 'rgba(0,0,0)',
		lineTension: 0,
		fill: false
	})

	let ctr = 0;
	for(let i = 4; i < 10; i++){

		key = `${2 ** i}-${2 ** (i+1)} Days`;

		ivChart.data.datasets.push({
			label: key,
			data: data[i],
			borderColor: colors[i - 4],
			lineTension: 0,
			fill: false
		})

	}

	ivChart.update();

}