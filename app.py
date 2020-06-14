from gevent.pywsgi import WSGIServer
from flask import render_template
from flask import request
from flask import Flask

from common.builder import Builder
from datetime import datetime
from hashlib import md5
import pandas as pd
import numpy as np
import json

###################################################################################################

TAS_COLS = [
	'username',
	'execution_time',
	'position_id',
	'option_id',
	'quantity'
]

PD_COLS = TAS_COLS[:3]
PD_COLS += ['direction', 'strategy', 'notes']

print("Initializing Builder Object")
builder_obj = Builder()
print("Builder Object Completed")

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

	password = builder_obj.connector.salt
	password = password.format(PASSWORD=data['password'])
	password = md5(password.encode()).hexdigest()

	if password != builder_obj.connector.get_password(data['username']):
		return json.dumps({
			"event" : "bad_password",
			"message" : f"Wrong password for user {data['username']}. Try Again."
		})

	position_keys = data['position_details'][0::2]
	position_qtys = data['position_details'][1::2]

	idc = np.argsort(position_keys)
	position_id = f"{position_keys[idc[0]]},{position_qtys[idc[0]]}"
	for idx in idc[1:]:
		position_id += f",{position_keys[idx]},{position_qtys[idx]}"
	position_id = md5(position_id.encode()).hexdigest()

	now = datetime.now()

	###############################################################################################

	items = [
		[data['username'], now, position_id, key, qty]
		for key, qty in zip(position_keys, position_qtys)
	]

	df = pd.DataFrame(items, columns = TAS_COLS)
	builder_obj.connector.write("timeandsales", df)

	###############################################################################################

	items = [
		items[0][:3] + [data['direction'], data['strategy'], data['notes']]
	]
	df = pd.DataFrame(items, columns = PD_COLS)
	builder_obj.connector.write("position_details", df)

	###############################################################################################

	return json.dumps({
		"event" : "success",
		"message" : "Position Added!"
	})

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 2608), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)
