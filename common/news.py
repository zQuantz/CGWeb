from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from common.utils.html import html
from urllib.parse import urlsplit
from hashlib import sha256
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
                timestamp_to=None, sentiment_greater=None, sentiment_lesser=None, sentiment_field=None,
                language=None, authors=None, categories=None, **kwargs):
    
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
        filters.append(terms_filter("article_source", authors))

    if categories:
        filters.append(terms_filter("categories", categories))

    if article_source:
        filters.append(terms_filter("article_source", article_source))

    if timestamp_from or timestamp_to:
        filters.append(range_filter("published_datetime", timestamp_from, timestamp_to))
        
    if sentiment_greater or sentiment_lesser:
        filters.append(range_filter(sentiment_field, sentiment_greater, sentiment_lesser))
    
    query['query']['function_score']['query']['bool']['filter'] = filters

    return query

def search_tweets(search_string="", sentiment=None, tickers=None, article_source=None, timestamp_from=None,
                timestamp_to=None, sentiment_greater=None, sentiment_lesser=None, sentiment_field=None, language=None,
                authors=None, hashtags=None, replies_count=None,retweets_count=None, likes_count=None, **kwargs):
    
    query = {
        "query" : {
            "function_score" : {
                "query" : {
                    "bool" : {}
                },
                "field_value_factor" : {
                    "field" : "timestamp",
                    "missing" : 0,
                    "factor" : 1
                }
            }                
        }
    }
    
    if search_string:
        query['query']['function_score']['query']['bool']['must'] = [
            {"match" : {"tweet" : search_string}}
        ]
    else:
    	query['sort'] = {
    		"timestamp" : {
    			"order" : "desc"
    		}
    	}

    filters = []
    
    if sentiment:
        filters.append(terms_filter("sentiment", sentiment))

    if tickers:
        filters.append(terms_filter("cashtags", tickers))

    if language:
        filters.append(terms_filter("language", language))

    if authors:
        filters.append(terms_filter("name", authors))
   
    if hashtags:
        filters.append(terms_filter("hashtags", hashtags))

    if timestamp_from or timestamp_to:
        filters.append(range_filter("timestamp", timestamp_from, timestamp_to))
        
    if sentiment_greater or sentiment_lesser:
        filters.append(range_filter(sentiment_field, sentiment_greater, sentiment_lesser))
	
    if replies_count:
        filters.append(range_filter("replies_count", replies_count))
	
    if retweets_count:
        filters.append(range_filter("retweets_count", retweets_count))
	
    if likes_count:
        filters.append(range_filter("likes_count", likes_count))
    
    query['query']['function_score']['query']['bool']['filter'] = filters

    return query

###################################################################################################

class News:

	def __init__(self):

		self.es = Elasticsearch(port=8607)
		# self.es = Elasticsearch()
		self.bm = {
			">" : "greater",
			"<" : "lesser"
		}
		self.bm_inv = {
			">" : "<",
			"<" : ">"
		}

	def search_news(self, params):

		query = search_news(**params)
		query['size'] = params['size']

		results = self.es.search(query, "news")
		_news_cards = self.generate_news(results['hits']['hits'], "news", "title", "link")

		query = search_tweets(**params)
		query['size'] = params['size']

		results = self.es.search(query, "tweets")
		_tweets_cards = self.generate_news(results['hits']['hits'], "tweets", "tweet", "name")

		cards = {
			"news" : _news_cards,
			"tweets" : _tweets_cards
		}
		hashs = {
			"news" : sha256(_news_cards.encode()).hexdigest(),
			"tweets" : sha256(_tweets_cards.encode()).hexdigest(),
		}

		return cards, hashs

	def generate_news(self, items, key, title_key, publisher_key):

		cards = []
		ctr = 0

		for i, item in enumerate(items):

			item = item['_source']
			title = item.get(title_key, None)
			if not title:
				continue

			summary = item.get("summary", None)

			if publisher_key == "link":

				link = item.get("link", "http://www..com")
				link_name = urlsplit(link).netloc.split(".")[1]
				if link_name == "com":
					link_name = urlsplit(link).netloc.split(".")[0]
				publisher = link_name.upper()

			else:

				publisher = item.get("name", "///").upper()
				link = item.get("link", "")

			time = item['published_datetime'] if key == 'news' else item['timestamp']
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
					"data-target" : f"#collapse{key}{ctr}",
					"aria-expanded" : "false",
					"aria-controls" : f"collapse{key}{ctr}"
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
				"id" : f"heading{key}{ctr}"
			})

			card_body = ""
			if summary:
				card_body = html("div", summary, {"class" : "card-body accordionCardBody"})
				card_body = html("div", card_body, {
						"id" : f"collapse{key}{ctr}",
						"class" : "collapse",
						"aria-labelledby" : f"heading{key}{ctr}",
						"data-parent" : "#newsAccordion"
					})

			card = html("div", card_header + card_body, {"class" : "card bg-dark fade-in"})
			
			cards.append(card)
			ctr += 1

		return "".join(cards)
