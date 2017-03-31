function left(){

	fetchConfig = {
    method: 'GET'
	};

	fetch('/left', fetchConfig)  
  .then(function(response) {

      		if (response.status !== 200) {  
        	console.log('Left Success' + response.status);  
        	return;  
      	}
		})
}

function center(){
		fetchConfig = {
    method: 'GET'
	};

	fetch('/center', fetchConfig)  
  .then(function(response) {

      		if (response.status !== 200) {  
        	console.log('Left Success' + response.status);  
        	return;  
      	}
		})
}

function right(){
		fetchConfig = {
    method: 'GET'
	};

	fetch('/right', fetchConfig)  
  .then(function(response) {

      		if (response.status !== 200) {  
        	console.log('Left Success' + response.status);  
        	return;  
      	}
		})
}

function getStatus(){
		
	fetchConfig = {
    method: 'get',
		headers: {
      'Accept': 'text/html',
      'Content-Type': 'text/html'
    }
	};

	fetch('/dividerStatus', fetchConfig)  
  .then(function(response) {
		return response.text();
	})
	.then(function(text){
		var statusArea = document.getElementById('dividerStatusDisplay');
		statusArea.innerHTML = "<b>Divider Status:</b></br></br></br><h1>" + text +"</h1>";
	})
}

function trafficData(){
	
	fetchConfig = {
    method: 'get',
		headers: {
      'Accept': 'application/json',
      'Content-Type': 'text/html'
    }
	};

	fetch('/trafficData', fetchConfig)  
  .then(function(response) {
		return response.json();
	})
	.then(function(jsonData){
		var trafficArea = document.getElementById('trafficTA');
		trafficArea.value = vkbeautify.json(JSON.stringify(jsonData),4);
	})
}

function resetTrafficData(){
		var trafficArea = document.getElementById('trafficTA');
		trafficArea.value = "";
}
    