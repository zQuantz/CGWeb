from datetime import datetime
import pandas as pd
import sys, os
import json

###################################################################################################

CONVERTER = {"M" : 1_000_000}
CONVERTER["B"] = CONVERTER["M"] * 1_000
CONVERTER["T"] = CONVERTER["B"] * 1_000
NUMBERS = ''.join([str(i) for i in range(10)])

###################################################################################################

DIR = os.path.realpath(os.path.dirname(__name__))

COLS = [
	"option_id",
	"volume",
	"open_interest",
	"bid_price",
	"option_price",
	"ask_price",
	"rho",
	"vega",
	"theta",
	"gamma",
	"delta",
	"implied_volatility",
	"strike_price",
]
COLS_FMT = [
	"Volume",
	"Open Int.",
	"Bid",
	"Price",
	"Ask",
	"Rho",
	"Vega",
	"Theta",
	"Gamma",
	"Delta",
	"I.V",
	"Strike"
]
COLS_FMT += COLS_FMT[::-1][1:]
IDXC, IDXP = 5, 17
PARSER = "lxml"

###################################################################################################

TAS_COLS = [
	'username',
	'execution_time',
	'ticker',
	'position_id',
	'option_id',
	'quantity',
	'option_type',
	'bid',
	'option_price',
	'ask',
	'delta',
	'gamma',
	'theta',
	'vega',
	'rho',
	'volume',
	'open_interest',
	'implied_volatility',
	'strike_price',
	'expiration_date',
	'time_to_expiry',
	'stock_price'
]

PT_COLS = TAS_COLS[:4]
PT_COLS += ['direction', 'strategy', 'sentiment', 'notes', 'image_filenames', 'images']

###################################################################################################

with open(f"{DIR}/config.json", "r") as file:
	CONFIG = json.loads(file.read())

with open(f"{DIR}/config_gcp.json", "r") as file:
	CONFIG_GCP = json.loads(file.read())

# with open(f"{DIR}/config.json", "w") as file:
# 	CONFIG['date'] = datetime.now().strftime("%Y-%m-%d")
# 	file.write(json.dumps(CONFIG))

###################################################################################################
