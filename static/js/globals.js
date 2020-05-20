
var options = null;
var position = null;

var stockPriceIdx = 11;
var stockPrice = 272.3;

var dMoneyness = "0.4";
var vMultiplier = 1;

function initGlobals(_options){

	var moneyness = document.getElementById("moneyness");
	var multiplier = document.getElementById("multiplier");
	var bottomRow = document.getElementById("bottomRow");

	position = new Position();
	options = _options;

}