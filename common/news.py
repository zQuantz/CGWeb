from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from common.utils.html import html
from urllib.parse import urlsplit
import pandas as pd
import numpy as np
import sys, os
import json

sentmap = {
	"positive" : "badge-success",
	"neutral" : "badge-secondary",
	"negative" : "badge-danger"
}

###################################################################################################

def terms_filter(field, value):

    return {"terms" : {field : value}}

def range_filter(field, gte=None, lte=None):

    _filter = {}

    if lte:
        _filter.update({"lte" : lte})

    if gte:
        _filter.update({"gte" : gte})

    return {"range" : {field : _filter}}

def search_news(search_string="", sentiment=None, tickers=None, article_source=None, timestamp_from=None,
                timestamp_to=None, sentiment_greater=None, sentiment_lesser=None, language=None, authors=None,
                categories=None):
    
    query = {
        "query" : {
            "function_score" : {
                "query" : {
                    "bool" : {}
                },
                "field_value_factor" : {
                    "field" : "published_datetime",
                    "missing" : 0,
                    "factor" : 1
                }
            }                
        }
    }
    
    if search_string:
        query['query']['function_score']['query']['bool']['must'] = [
            {"match" : {"search" : search_string}}
        ]
    else:
    	query['sort'] = {
    		"published_datetime" : {
    			"order" : "desc"
    		}
    	}

    filters = []
    if sentiment:
        filters.append(terms_filter("sentiment", sentiment))

    if tickers:
        filters.append(terms_filter("tickers", tickers))

    if language:
        filters.append(terms_filter("language", language))

    if authors:
        filters.append(terms_filter("authors", tickers))

    if categories:
        filters.append(terms_filter("categories", categories))

    if article_source:
        filters.append(terms_filter("article_source", article_source))

    if timestamp_from or timestamp_to:
        filters.append(range_filter("published_datetime", timestamp_from, timestamp_to))
        
    if sentiment_greater or sentiment_lesser:
        filters.append(range_filter("sentiment_score", sentiment_greater, sentiment_lesser))
    
    query['query']['function_score']['query']['bool']['filter'] = filters

    return query

###################################################################################################

class News:

	def __init__(self):

		self.reset()
		self.es = Elasticsearch(port=8607)

	def reset(self):

		self.cards = []
		self.ctr = 0

	def search_news(self, params):

		query = search_news(**params)
		query['size'] = 100

		results = self.es.search(query, "news")
		self.generate_news(results['hits']['hits'])

	def generate_news(self, items):

		for i, item in enumerate(items):

			item = item['_source']
			title = item.get("title", None)
			if not title:
				continue

			summary = item.get("summary", None)
			author = item.get("author", "")

			link = item.get("link", "http://www..com")
			link_name = urlsplit(link).netloc.split(".")[1]
			if link_name == "com":
				link_name = urlsplit(link).netloc.split(".")[0]
			link_name = link_name.upper()

			if author == "":
				publisher = link_name
			else:
				publisher = "  /  ".join([link_name, author])

			time = item['published_datetime']
			try:
				time = datetime.strptime(time, "%Y-%d-%mT%H:%M:%S")
			except:
				time = datetime.strptime(time, "%Y-%m-%dT%H:%M:%S")

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

			sentiment = item.get("sentiment", None)
			sentiment_score = item.get("sentiment_score", None)
			if sentiment:
				sentiment_badge = html("span", f"{sentiment.capitalize()} / {round(sentiment_score * 100, 0)}%", {
					"class" : f"badge {sentmap[sentiment]} newsTag"
				})
			else:
				sentiment_badge = ""

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
				sentiment_badge,
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
			self.ctr += 1

		if len(self.cards) != 0:
			self._cards = "".join(self.cards)
		else:
			self._cards = None
