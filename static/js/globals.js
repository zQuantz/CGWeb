
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

}