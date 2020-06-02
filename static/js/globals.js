
var options = null;
var position = null;
var position_info = null;

var stockPriceIdx = 11;
var stockPrice = 316.73;

var dMoneyness = "0.4";
var vMultiplier = 1;

function initGlobals(_options, _position_info){

	var moneyness = document.getElementById("moneyness");
	var multiplier = document.getElementById("multiplier");
	var bottomRow = document.getElementById("bottomRow");

	position = new Position();
	position_info = _position_info;
	options = _options;

	var ctx = document.getElementById('riskGraph').getContext('2d');
	var chart = new Chart(ctx, {
		
		type: 'line',
		
		data: {
			datasets: [{
				label: 'Scatter Dataset',
				data: [{
					x: -10,
					y: 0
				}, {
					x: 0,
					y: 10
				}, {
					x: 10,
					y: 5
				}]
			}]
		},

		// data: {
		//     labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
		//     datasets: [{
		//         backgroundColor: undefined,
		//         borderColor: "#45ff17",
		//         data: [0, 10, 5, 2, 20, 30, 45]
		//     }]
		// },
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
					radius:5,
					hitRadius:10,
					hoverRadius:2,
					pointStyle:'line'
				},

			},

			scales: {
				xAxes: [{
					type: 'linear',
					position: 'bottom'
				}]
			}
		}
	});

}