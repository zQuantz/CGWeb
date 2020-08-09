from common.calculator import calculate_greeks

from gevent.pywsgi import WSGIServer
from flask import render_template
from datetime import datetime
from flask import request
from flask import Flask

from common.connector import Connector
from common.scenarios import Scenarios
from common.builder import Builder

import json

###################################################################################################

print("Initializing Builder Object")
connector = Connector()
builder_obj = Builder(connector)
scenarios_obj = Scenarios(connector)
print("Builder Object Completed")

input_values = {
	key : ""
	for key in ["S", "K", "IV", "t", "r", "q", "type"]
}

app = Flask(__name__)

###################################################################################################

@app.after_request
def after_request(response):
	response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, public, max-age=0"
	response.headers["Expires"] = 0
	response.headers["Pragma"] = "no-cache"
	return response

@app.route("/")
@app.route("/builder")
def builder():

	ticker = request.args.get('ticker', None)
	date = request.args.get('date', None)

	print("ticker", ticker)
	print("date", date)

	builder_obj.fetch_ticker(ticker, date)

	return render_template("builder.html", name=ticker, builder=builder_obj, connector=connector)

@app.route("/update", methods=["POST"])
def update():

	status = connector.update()

	if status:

		item = json.dumps({
			"status" : status,
			"ticker_dates" : connector.ticker_dates,
			"unique_dates" : connector.unique_dates,
			"ticker_options" : connector._ticker_options
		})

	else:

		item = json.dumps({
			"status" : status
		})


	return item

@app.route("/execute", methods=["POST"])
def execute():

	data = json.loads(request.get_data())
	return json.dumps(builder_obj.execute(data))

###################################################################################################

@app.route("/calculator")
def calculator():

	greeks = None
	if request.args.get("S"):
		greeks = calculate_greeks(request.args)
		input_values.update(dict(request.args))

	return render_template("calculator.html", greeks = greeks, input_values = input_values)

@app.route("/scenarios", methods=["GET", "POST"])
def scenarios():

	if request.method == "POST":

		data = json.loads(request.get_data())

		if type(data) is dict and data.get('reset'):
			return json.dumps({})

		scenarios_obj.generate_scenarios(data)
		return json.dumps({
			"position_rows" : scenarios_obj._position_rows,
			"position_attributions" : scenarios_obj.position_attributions
		})

	else:

		scenarios_obj.generate_option_ids(request.args.getlist("tickers"))
		scenarios_obj._position_rows = None

	today = datetime.now().strftime("%Y-%m-%d")
	return render_template("scenarios.html", scenarios = scenarios_obj, connector = connector, today = today)

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 2608), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)
