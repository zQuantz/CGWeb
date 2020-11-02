
function init(){

	setInterval(fetch_news, 5000);

}

function fetch_news(){

	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {

		if(this.readyState == 4 && this.status == 200){

			let data = JSON.parse(this.responseText);
			let newsAccordion = $("#newsAccordion");
			data.cards.forEach(card => {
				newsAccordion.prepend(card);
			})

		}

	}

	request.open("GET", "/news_update");
	request.send();

}