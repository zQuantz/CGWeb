
class Position {
	constructor(){
		this.options = {};
		this.size = 0;
		this.setAggregates();
		this.riskGraphData = [];
	}

	setAggregates(){
		this.totalPremium = 0;
		this.totalPctPremium = 0;
		this.totalDeltaShares = 0;
		this.totalDeltaDollars = 0;
		this.totalVegaDollars = 0;
		this.totalThetaDollars = 0;
	}
	calculateRiskGraphData(){

		this.riskGraphData = [];
		if (this.size == 0)
			return;

		let bnum = Math.min(uChangeVals.current, 100);
		for(let i = bnum * 10; i >= -uChangeVals.current * 10; i--){
			
			let price = stockPrice - i * priceIncrement;
			let payoff = 0;
			
			for(const key in this.options){
				payoff += this.options[key].getPayoff(price);
			}

			this.riskGraphData.push({
				x: Math.round(price * 100) / 100,
				y: Math.round(payoff * 100) / 100
			})

		}

	}

}

class Option {
	constructor(option, quantity, cost, type){
		this.option = option;
		this.quantity = quantity;
		this.cost = cost;
		this.type = type;
	}
	getPayoff(price){
		let payoff = this.type * (price - this.option.strike_price);
		payoff = Math.max(payoff, 0) - this.cost;
		payoff *= this.quantity;
		return payoff;
	}
}

function numberFormat(num, p, symbol){
	
	let anum = Math.abs(num);
	let f = Math.pow(10, p);
	let m = "";

	if (anum >= 1000000){
		num /= 1000000;
		m = "M"
	}
	else if (anum >= 1000){
		num /= 1000;
		m = "K"	
	}

	num = Math.round(num * f) / f;
	return num.toLocaleString() + m + symbol;

}

function displayPositions(){

	let table = $("#positionInfoTable tbody");
	let summaryTable = $("#executionSummaryTable tbody");
	let idx = 1;

	table.empty();
	summaryTable.empty();

	position.setAggregates();

	for(key in position.options){
		
		let option = position.options[key];

		let newRow = position_info.option_row;
		let summaryRow = position_summary.summary_row;
		summaryRow = summaryRow.replace("NUM", idx);

		newRow = newRow.replace("OPTION_ID", key);
		newRow = newRow.replace("OPTION_ID", key);
		summaryRow = summaryRow.replace("OPTION_ID", key)

		let qty = option.quantity;
		qty = qty.toLocaleString();
		newRow = newRow.replace("QUANTITY", qty);
		summaryRow = summaryRow.replace("QUANTITY", qty);

		let cost = option.cost;
		cost = numberFormat(cost, 2, "$");
		newRow = newRow.replace("COST_PER_UNIT", cost);
		summaryRow = summaryRow.replace("PREMIUM", cost);

		let premium = option.quantity * option.cost * 100;
		position.totalPremium += premium;
		premium = numberFormat(premium, 2, "$");
		newRow = newRow.replace("PREMIUM", premium);
		summaryRow = summaryRow.replace("NET_PREMIUM", premium);

		let iv = option.option.implied_volatility * 100;
		iv = numberFormat(iv, 2, "%");		
		newRow = newRow.replace("I.V.", iv);

		let moneyness = 100 * option.option.strike_price / stockPrice;
		moneyness = numberFormat(moneyness, 2, "%");		
		newRow = newRow.replace("MONEYNESS", moneyness);
		
		let pct_premium = option.cost / stockPrice * 100;
		position.totalPctPremium += pct_premium * option.quantity;
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
		summaryTable.append(summaryRow);

		idx+=1;

	}

	for(let i = position.size; i < 4; i++)
		table.append(position_info.empty_option_row);

	if (position.size == 0){
		table.append(position_info.empty_agg_row);
		summaryTable.append(position_summary.empty_agg_row);
		modalExecuteButton.disabled = true;
		return;
	}

	let aggregateRow = position_info.agg_row;
	let aggregateSummaryRow = position_summary.agg_row;
	modalExecuteButton.disabled = false;

	let value = position.totalPremium;
	value = numberFormat(value, 2, "$");
	aggregateRow = aggregateRow.replace("TOTAL_PREMIUM", value);
	aggregateSummaryRow = aggregateSummaryRow.replace("TOTAL_PREMIUM", value);

	value = position.totalPctPremium;
	value = numberFormat(value, 2, "%");
	aggregateRow = aggregateRow.replace("TOTAL_PCT_PREMIUM", value);

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
	summaryTable.append(aggregateSummaryRow);

}

function displayRiskGraph(){
	position.calculateRiskGraphData();
	riskGraph.data.datasets.forEach((dataset) => {
		dataset.data = position.riskGraphData;
	});
	riskGraph.update();
}

function addToPosition(direction, option_id){

	let netQty = direction * multiplierVals.current;
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
			direction > 0 ? option.ask : option.bid,
			option.option_type == "C" ? 1 : -1);
		position.size += 1;

	}

	displayPositions();
	onChangeUChange();

}

function removeFromPosition(option_id){

	delete position.options[option_id];
	position.size -= 1;
	displayPositions();
	onChangeUChange();

}

function executePosition(){

	let username = $("#executeUsernameSelect").val();
	let password = $("#executePasswordInput").val();

	let direction = $("#executeDirectionSelect").val();
	let strategy = $("#executeStrategySelect").val();

	let sentiment = $("#executeSentimentSelect").val();
	let notes = $("#executionTradeNotes").val();

	ajax({
		url: "/execute",
		type: "POST",
		data: JSON.stringify({
			username: username,
			password: password,
			direction: direction,
			strategy: strategy,
			sentiment: sentiment,
			notes: notes,
			options: position.options,
			filenames: imageFileNames,
			images: b64Images
		}),
		beforeSend: function() {},
        complete: function () {},
        success: function(response){

        	response = JSON.parse(response);

        	let classes = [
        		"badge-success",
        		"badge-danger",
        		"badge-secondary"
        	];
        	modalStatusBadge.classList.remove(...classes);

        	if (response.event == "bad_password"){

        		modalStatusBadge.classList.add("badge-danger");
        		modalStatusBadge.innerText = response.message;
        		return;

        	}

        	modalStatusBadge.classList.add("badge-success");
        	modalStatusBadge.innerText = response.message;

        	position = new Position();
        	displayPositions()
        	onChangeUChange();

        	resetExecuteModal();

        },
        error: function(error){
        	console.log("Damn!", error);
        }
    });

}