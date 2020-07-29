var actionEntryTbody = null;
var startDateInput = null;
var optionSelect = null;
var endDateInput = null;
var tr = null;

var positions = [];
var position = {};

var minDate = "2019-12-01";

function init(tr_){

	actionEntryTbody = $("#actionEntryTbody");

	optionSelect = $("#optionSelect");
	optionSelect.change(editPosition);

	tr = tr_;

	startDateInput = $("#startDateInput");
	endDateInput = $("#endDateInput");

	let date = new Date().toISOString().split("T")[0]
	startDateInput.attr("max", date);
	startDateInput.attr("max", date);

	startDateInput.change(function() {
		endDateInput.attr("min", startDateInput.val())
	});

}

function removePosition(e){

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

	actionEntryTbody.empty();

	options = optionSelect.val();
	options.forEach( (option, ctr) => {

		newPosition[option] = 0;

		let ntr = tr.replace("OPTION_ID", option);
		ntr = ntr.replace("OPTION_ID", option);

		actionEntryTbody.append(ntr);

		if(option in position){
			newPosition[option] = position[option];
		}

		$("#actionEntryTbody input:last").val(newPosition[option]);

	})

	position = newPosition;

}

function resetPosition() {

	position = {};
	
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
		endDate: endDateInput.val()
	})
	resetPosition();

}