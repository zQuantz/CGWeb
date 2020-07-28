from common.calculator import calculate_greeks
from gevent.pywsgi import WSGIServer
from flask import render_template
from flask import request
from flask import Flask

from common.builder import Builder
import json

###################################################################################################

print("Initializing Builder Object")
builder_obj = Builder()
print("Builder Object Completed")

input_values = {
	key : ""
	for key in ["S", "K", "IV", "t", "r", "q", "type"]
}

###################################################################################################

app = Flask(__name__)

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

	return render_template("index.html", name=ticker, builder=builder_obj)

@app.route("/update", methods=["POST"])
def update():

	status = builder_obj.update()

	if status:

		item = json.dumps({
			"status" : status,
			"unique_dates" : builder_obj.unique_dates,
			"ticker_dates" : builder_obj.ticker_dates,
			"ticker_options" : builder_obj._ticker_options
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

@app.route("/calculators")
def calculator():

	greeks = None
	if request.args.get("S"):
		greeks = calculate_greeks(request.args)
		input_values.update(dict(request.args))

	return render_template("calculators.html", greeks = greeks, input_values = input_values)

@app.route("/scenarios")
def scenarios():
	return render_template("scenarios.html")

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 2608), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)
