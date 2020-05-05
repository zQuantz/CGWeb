from gevent.pywsgi import WSGIServer
from flask import render_template
from flask import request
from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello():
	return "Hello,World!"

@app.route("/builder")
def builder():

	ticker = request.args.get('ticker', None)
	date = request.args.get('date', None)

	print("ticker", ticker)
	print("date", date)

	return render_template("index.html", name=ticker)

if __name__ == '__main__':

	try:
		http_server = WSGIServer(('', 5000), app)
		http_server.serve_forever()
	except Exception as e:
		print(e)