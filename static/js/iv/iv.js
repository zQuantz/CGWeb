var ivChart = null;
var surface = null;
var chartLog = {};

var colors = [
	'rgba(0,0,0)',
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

function addToChart(label, id){

	chartLog[id] = ivChart.data.datasets.length;
	ivChart.data.datasets.push({
		label: label,
		data: surface[id],
		borderColor: colors[chartLog[id] % colors.length],
		lineTension: 0,
		fill: false
	})

	ivChart.update();

}

function removeFromChart(id){

	ivChart.data.datasets.splice(chartLog[id], 1);
	ivChart.update()

	for (key in chartLog){
		if (chartLog[key] > chartLog[id])
			chartLog[key] -= 1
	}

	delete chartLog[id];

}

function init(){

	$('#ivSelectorPopover').popover({
		content: $("#ivSelectorTableContent table"),
		html: true
	});

	$("#ivSelectorTable td button").click(function () {

		if (this.classList.contains("ivSelectButtonActive")){
			this.classList.remove("ivSelectButtonActive");
			removeFromChart(this.id);
		}
		else {
			this.classList.add("ivSelectButtonActive");
			addToChart(this.innerText, this.id);
		}
	})

	let ctx = document.getElementById(`ivChart`).getContext('2d');
	ivChart = new Chart(ctx, {

		type: 'line',
		data: {
			datasets: []
		},
		options: {

			title: {
				display: true,
				text: "Historical IV",
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
						return item[0].label;
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

function initTicker(_surface, symbol) {

	surface = _surface;

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

	ivChart.data.labels = surface.date_current;
	addToChart('3M 100%', "m3m100");
	$("#m3m100").addClass("ivSelectButtonActive");

}