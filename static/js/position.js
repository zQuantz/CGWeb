
class Position {
	constructor(){
		this.options = {};
		this.size = 0;
		this.setAggregates();
	}

	setAggregates(){
		this.totalPremium = 0;
		this.totalDeltaShares = 0;
		this.totalDeltaDollars = 0;
		this.totalVegaDollars = 0;
		this.totalThetaDollars = 0;
	}

}

class Option {
	constructor(option, quantity, cost){
		this.option = option;
		this.cost = cost;
		this.quantity = quantity;
	}
	getPayoff(price){
		let payoff = price - this.option.strike_price;
		payoff = Math.max(payoff, 0) - this.cost;
		payoff *= this.quantity;
		return payoff;
	}
}

function numberFormat(num, p, symbol){
	
	let f = Math.pow(10, p);
	let m = "";

	if (num >= 100000){
		num /= 1000;
		m = "K"
	}

	num = Math.round(num * f) / f;
	return num.toLocaleString() + m + symbol;

}

function displayPositions(){

	let table = $(".infoTable tbody")
	table.empty()

	position.setAggregates();

	for(key in position.options){
		
		let option = position.options[key];
		let newRow = position_info.option_row;

		newRow = newRow.replace("OPTION_ID", key);
		newRow = newRow.replace("OPTION_ID", key);

		let qty = option.quantity;
		qty = qty.toLocaleString();
		newRow = newRow.replace("QTY", qty);

		let cost = option.cost;
		cost = numberFormat(cost, 2, "$");
		newRow = newRow.replace("COST_PER_UNIT", cost);

		let premium = option.quantity * option.cost * 100;
		position.totalPremium += premium;
		premium = numberFormat(premium, 2, "$");
		newRow = newRow.replace("PREMIUM", premium);

		let iv = option.option.implied_volatility * 100;
		iv = numberFormat(iv, 2, "%");		
		newRow = newRow.replace("IV", iv);

		let moneyness = 100 * option.option.strike_price / stockPrice;
		moneyness = numberFormat(moneyness, 2, "%");		
		newRow = newRow.replace("MONEYNESS", moneyness);
		
		let pct_premium = option.cost / stockPrice * 100;
		pct_premium = numberFormat(pct_premium, 2, "%");		
		newRow = newRow.replace("PCT_PREMIUM", pct_premium);

		let deltaShares = option.option.delta * option.quantity * 100;
		position.totalDeltaShares += deltaShares;

		let deltaDollars = deltaShares * stockPrice;
		position.totalDeltaDollars += deltaDollars;

		deltaShares = numberFormat(deltaShares, 0, "");		
		newRow = newRow.replace("DELTA_SHARES", deltaShares);

		deltaDollars = numberFormat(deltaDollars, 2, "$");		
		newRow = newRow.replace("DELTA_$", deltaDollars);

		let vegaDollars = option.option.vega * option.quantity * 100;
		position.totalVegaDollars += vegaDollars;
		vegaDollars = numberFormat(vegaDollars, 2, "$");
		newRow = newRow.replace("VEGA_$", vegaDollars);

		let thetaDollars = option.option.theta * option.quantity * 100;
		position.totalThetaDollars += thetaDollars;
		thetaDollars = numberFormat(thetaDollars, 2, "$");
		newRow = newRow.replace("THETA_$", thetaDollars);

		table.append(newRow);

	}

	for(let i = position.size; i < 4; i++)
		table.append(position_info.empty_option_row);

	if (position.size == 0){
		table.append(position_info.empty_agg_row);
		return;
	}

	let aggregateRow = position_info.agg_row;

	let value = position.totalPremium;
	value = numberFormat(value, 2, "$");
	aggregateRow = aggregateRow.replace("TOTAL_PREMIUM", value);

	value = position.totalDeltaShares;
	value = numberFormat(value, 0, "");
	aggregateRow = aggregateRow.replace("TOTAL_DELTA_SHARES", value);

	value = position.totalDeltaDollars;
	value = numberFormat(value, 2, "$");
	aggregateRow = aggregateRow.replace("TOTAL_DELTA_$", value);

	value = position.totalVegaDollars;
	value = numberFormat(value, 2, "$");
	aggregateRow = aggregateRow.replace("TOTAL_VEGA_$", value);

	value = position.totalThetaDollars;
	value = numberFormat(value, 2, "$");
	aggregateRow = aggregateRow.replace("TOTAL_THETA_$", value);

	table.append(aggregateRow);

}

function addToPosition(direction, option_id){

	let netQty = direction * vMultiplier;
	if (option_id in position.options){

		if (netQty + position.options[option_id].quantity == 0){
			delete position.options[option_id];
			position.size -= 1;
		}
		else
			position.options[option_id].quantity += netQty;
	
	}
	else {
	
		let option = options[option_id];
		position.options[option_id] = new Option(option, netQty,
							  					 direction > 0 ? option.ask : option.bid);
		position.size += 1;

	}

	displayPositions();

}

function removeFromPosition(option_id){

	delete position.options[option_id];
	position.size -= 1;
	displayPositions();

}