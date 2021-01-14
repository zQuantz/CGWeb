from common.calculator import calculate_greeks, empty_table

from datetime import datetime, timedelta
from gevent.pywsgi import WSGIServer
from flask import render_template
from flask import request
from flask import Flask

from common.connector import Connector
from common.scenarios import Scenarios
from common.monitor import Monitor
from common.surface import Surface
from common.density import Density
from common.builder import Builder
from common.news import News
from common.iv import IV

import json

###################################################################################################

print("Initializing Builder Object")
connector = Connector()

iv_obj = IV(connector)
monitor_obj = Monitor(connector)
surface_obj = Surface(connector)
builder_obj = Builder(connector)
density_obj = Density(connector)
scenarios_obj = Scenarios(connector)
news_obj = News()

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

@app.route("/builder")
def builder():

	ticker = request.args.get('ticker', None)
	date = request.args.get('date', None)

	print("ticker", ticker)
	print("date", date)

	builder_obj.fetch_ticker(ticker, "LIVE" if not date else date)

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

@app.route("/")
@app.route("/monitor")
def monitor():

	yday = (datetime.now() - timedelta(days=1))
	params = {
		"ticker_list" : request.args.get("tickerList", "main"),
		"term_one" : request.args.get("termOne", 3),
		"term_two" : request.args.get("termTwo", 12),
		"down_strike" : request.args.get("downStrike", 90),
		"up_strike" : request.args.get("upStrike", 110),
		"lookback" : request.args.get("lookback", 6),
		"end_date" : request.args.get("endDate", yday.strftime("%Y-%m-%d"))
	}

	monitor_obj.params = params
	monitor_obj.calculate_monitor(**params)
	return render_template("monitor.html", monitor = monitor_obj, connector = connector)

@app.route("/calculator")
def calculator():

	greeks = None
	if request.args.get("S"):
		greeks = calculate_greeks(request.args)
		input_values.update(dict(request.args))

	return render_template("calculator.html", greeks = greeks, input_values = input_values, empty_table = empty_table)

@app.route("/scenarios", methods=["GET", "POST"])
def scenarios():

	if request.method == "POST":

		data = json.loads(request.get_data())

		if type(data) is dict and data.get('reset'):
			scenarios_obj.reset()
			return json.dumps({})

		scenarios_obj.generate_scenarios(data)
		return json.dumps({
			"position_rows" : scenarios_obj._position_rows,
			"position_attributions" : scenarios_obj.position_attributions
		})

	else:

		scenarios_obj.generate_option_ids(request.args.getlist("tickers"))

	today = datetime.now().strftime("%Y-%m-%d")
	return render_template("scenarios.html", scenarios = scenarios_obj, connector = connector, today = today)

@app.route("/iv")
def iv():

	iv_obj.get_surface(request.args.get("ticker"))
	return render_template("iv.html", iv = iv_obj, connector = connector)

@app.route("/surface")
def surface():

	ticker = request.args.get('ticker', None)
	date = request.args.get('date', None)

	print("ticker", ticker)
	print("date", date)

	surface_obj.get_surface(ticker, date)
	return render_template("surface.html", surface = surface_obj, connector = connector)

@app.route("/density")
def density():

	ticker = request.args.get('ticker', None)
	date = request.args.get('date', None)

	print("ticker", ticker)
	print("date", date)

	density_obj.get_risk_neutral_density(ticker, date)
	return render_template("density.html", density = density_obj, connector = connector)

@app.route("/news", methods=["GET"])
def news():

	params = {}
	args = request.args

	if args.get('searchString', None):
		params['search_string'] = args.get('searchString')

	if args.get('tickers', None):
		params['tickers'] = args.get('tickers').split(",")

	if args.get('categories', None):
		params['categories'] = args.get('categories').split(",")

	if args.get('startDate', None):
		params['timestamp_from'] = args.get('startDate')

	if args.get('endDate', None):
		params['timestamp_to'] = args.get('endDate')

	if args.get('sentimentValue', None):
		params[f'sentiment_{args.get("sentimentBoundary")}'] = float(args.get('sentimentValue')) / 100

	news_obj.params = dict(args)
	news_obj.reset()
	news_obj.search_news(params)

	return render_template("news.html", news = news_obj)

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 2608), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)
