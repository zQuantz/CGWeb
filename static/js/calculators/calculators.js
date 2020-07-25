var sensitivityChart = null;

var option_dropdown = null;
var xvar_dropdown = null;
var yvar_dropdown = null;

var n_increments = null;
var n_options = null;
var options = null;
var names = null;

var colors = [
	'rgba(255,0,0)',
 	'rgba(0,255,0)',
 	'rgba(0,0,255)',
 	'rgba(255,255,0)',
 	'rgba(0,255,255)',
 	'rgba(255,0,255)',
 	'rgba(192,192,192)',
 	'rgba(128,128,128)',
 	'rgba(128,0,0)',
 	'rgba(128,128,0)',
 	'rgba(0,128,0)',
 	'rgba(128,0,128)',
 	'rgba(0,128,128)',
 	'rgba(0,0,128)'
 ];

function init(greeks){

	option_dropdown = document.getElementById("optionSelect");
	xvar_dropdown = document.getElementById("xSelect");
	yvar_dropdown = document.getElementById("ySelect");

	n_increments = greeks['n_increments'];
	n_options = greeks['n_options'];
	options = greeks['options'];
	names = greeks['names'];

	initChart();

	option_dropdown.addEventListener("change", updateChart);
	xvar_dropdown.addEventListener("change", updateChart);
	yvar_dropdown.addEventListener("change", updateChart);

	updateChart();

}

function initChart(){

	var ctx = document.getElementById('sensitivityChart').getContext('2d');
	sensitivityChart = new Chart(ctx, {
		
		type: 'line',
		
		data: {
			datasets: []
		},
		options: {
			
			title: {
				display:true,
				text:"Sensitivity Chart",
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

	});
}

function updateChart(){

	let oids = $("#optionSelect").val();
	let xvar = xvar_dropdown.value;
	let yvar = yvar_dropdown.value;

	sensitivityChart.data.datasets = [];

	oids.forEach( (oid, idx) => {

		row_offset = oid * n_increments * 6 + n_increments * xvar;

		let data = [];
		for(let i = 0; i < n_increments; i++){

			data.push({
				y: Math.round(options[row_offset + i][yvar] * 1000000) / 1000000,
				x: Math.round(options[row_offset + i][xvar] * 1000000) / 1000000
			})

		}

		sensitivityChart.data.datasets.push({
			label: `ID: ${oid}`,
			data: data,
			borderColor: colors[idx],
			backgroundColor: 'rgba(52, 58, 64, 0.15)'
		});

		sensitivityChart.options.scales.xAxes[0].scaleLabel.labelString = names[xvar];
		sensitivityChart.options.scales.yAxes[0].scaleLabel.labelString = names[yvar];

	})

	sensitivityChart.update();

}