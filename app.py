from gevent.pywsgi import WSGIServer
from flask import render_template
from flask import request
from flask import Flask

from common.builder import Builder
import pandas as pd
import json

###################################################################################################

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

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 2608), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)
