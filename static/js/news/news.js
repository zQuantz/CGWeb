
function init(){

	setInterval(fetch_news, 15_000);

}

function fetch_news(){

	var request = new XMLHttpRequest();
	request.onreadystatechange = function() {

		if(this.readyState == 4 && this.status == 200){

			let data = JSON.parse(this.responseText);
			let newsAccordion = $("#newsAccordion");
			data.cards.forEach(card => {
				$(card).hide().prependTo("#newsAccordion").show();
			})

		}

	}

	request.open("GET", "/news_update");
	request.send();

}