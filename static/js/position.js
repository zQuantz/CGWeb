
class Position {
	constructor(){
		this.options = {};
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

function addToPosition(direction, option_id){

	let netQty = direction * vMultiplier;
	if (option_id in position.options){

		if (netQty + position.options[option_id].quantity == 0)
			delete position.options[option_id];
		else
			position.options[option_id].quantity += netQty;
	
	}
	else {
	
		let option = options[option_id];
		position.options[option_id] = new Option(option, netQty,
							  					 direction > 0 ? option.ask : option.bid);
	
	}
}