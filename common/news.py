from datetime import datetime, timedelta
from common.utils.html import html
from urllib.parse import urlsplit
from socket import gethostname
from hashlib import sha256
import pandas as pd
import numpy as np
import sys, os
import json

hostname = gethostname()
if hostname == 'zQ':
	NEWS_DIR = f"/home/zquantz/OscraP/rss/news_data"
else:
	NEWS_DIR = f"/home/zqretrace/OscraP/rss/news_data"

class News:

	def __init__(self):

		self.reset()

	def reset(self):

		self.ctr = 0
		self.files = set(['.gitignore'])
		self.items = set()
		self.cards = []
		self.times = []

	def fetch_news(self):

		new_files = set(os.listdir(NEWS_DIR)).difference(self.files)
		
		items = []
		for new_file in new_files:

			with open(f"{NEWS_DIR}/{new_file}", "r") as file:

				try:
					items.extend(json.loads(file.read()))
					self.files.add(new_file)
				except Exception as e:
					print(e)

		if len(items) != 0:
			self.generate_news(items)

	def generate_news(self, items):

		for i, item in enumerate(items):

			print(i)

			title = item.get("title", None)
			if not title:
				continue

			summary = item.get("summary", None)
			author = item.get("author", "")

			dummy_item = {
				"title" : title,
				"summary" : summary,
				"author" : author
			}
			dummy_item = json.dumps(dummy_item, sort_keys = True)
			hash_ = sha256(dummy_item.encode()).hexdigest()

			if hash_ in self.items:
				continue

			link = item.get("link", "http://www..com")
			link_name = urlsplit(link).netloc.split(".")[1]
			link_name = link_name.upper()

			if author == "":
				publisher = link_name
			else:
				publisher = "  /  ".join([link_name, author])

			time = item['oscrap_acquisition_datetime']
			time = datetime.strptime(time, "%Y-%d-%m %H:%M:%S.%f")
			time = time - timedelta(hours=5)
			_time = int(time.timestamp())
			time = time.strftime("%Y-%d-%m %H:%M:%S")

			time_badge = html("span", time, {"class" : "badge badge-secondary newsTag"})
			publisher_badge = html("a", publisher, {
				"href" : link,
				"class" : "badge badge-primary newsTag",
				"target" : "_blank",
				"rel" : "noopener noreferrer"
			})
			sentiment_badge = html("span", "Sentiment", {"class" : "badge badge-danger newsTag"})
			brs = "<br><br>"

			card_header = html("button", title, {
					"class" : "btn btn-link accordionButton",
					"type" : "button",
					"data-toggle" : "collapse",
					"data-target" : f"#collapse{self.ctr}",
					"aria-expanded" : "false",
					"aria-controls" : f"collapse{self.ctr}"
			})
			card_header = "".join([
				time_badge,
				publisher_badge,
				# sentiment_badge,
				brs,
				card_header
			])
			card_header = html("h5", card_header, {"class" : "mb-0 accordionTab"})
			card_header = html("div", card_header, {
				"class" : "card-header",
				"id" : f"heading{self.ctr}"
			})

			card_body = ""
			if summary:
				card_body = html("div", summary, {"class" : "card-body accordionCardBody"})
				card_body = html("div", card_body, {
						"id" : f"collapse{self.ctr}",
						"class" : "collapse",
						"aria-labelledby" : f"heading{self.ctr}",
						"data-parent" : "#newsAccordion"
					})

			card = html("div", card_header + card_body, {"class" : "card bg-dark fade-in"})
			
			self.cards.append(card)
			self.times.append(_time)

			self.ctr += 1
			self.items.add(hash_)

		idc = np.argsort(self.times)
		self.times = [self.times[idx] for idx in idc]
		self.cards = [self.cards[idx] for idx in idc]
