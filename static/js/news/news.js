var tweetsAccordion = undefined;
var newsAccordion = undefined;

var params = undefined;
var hashs = undefined;

function init(_params, _hashs){

	tweetsAccordion = $("#tweetsAccordion");
	newsAccordion = $("#newsAccordion");

	params = _params;
	hashs = _hashs;

	setInterval(fetch_news, 5_000);

}

function fetch_news(){

	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {

		if(this.readyState == 4 && this.status == 200){

			let data = JSON.parse(this.responseText);

			if (hashs.news != data.hashs.news) {
				newsAccordion.empty()
				newsAccordion.append(data.cards.news)
				hashs.news = data.hashs.news;
			}

			if (hashs.tweets != data.hashs.tweets) {
				tweetsAccordion.empty()
				tweetsAccordion.append(data.cards.tweets)
				hashs.tweets = data.hashs.tweets;
			}

		}

	}

	request.open("POST", "/news_update");
	request.send(JSON.stringify(params));

}