var actionEntryTbody = null;
var optionSelect = null;
var tr = null;

var position = {};

function init(tr_){

	console.log(tr);

	actionEntryTbody = $("#actionEntryTbody");
	optionSelect = $("#optionSelect");
	tr = tr_;

	optionSelect.change(editPosition);

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