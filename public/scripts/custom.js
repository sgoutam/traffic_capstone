
function trafficData(){
		var request = new XMLHttpRequest();
		var datapointsUrl = "/v1/assets/1000000018/events?event-types=TFEVT&start-ts=1453766605577&end-ts=1453772603879&size=10&page=1";
		request.open('GET', datapointsUrl, true);
		request.onload = function() {
				var data = request.responseText;
				console.log(data);
    }
  }
