from datetime import datetime
import sys, os
import json

DIR = os.path.realpath(os.path.dirname(__name__))

with open(f"{DIR}/config.json", "r") as file:
	CONFIG = json.loads(file.read())

with open(f"{DIR}/config.json", "w") as file:
	CONFIG['date'] = datetime.now().strftime("%Y-%m-%d")
	file.write(json.dumps(CONFIG))
