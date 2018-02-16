window.onload = function() {
	console.log('Program started');
	var div = document.getElementById('program-log');

	setInterval(function() {
		div.innerHTML += '<br\>Program is still alive.'
	}, 1000);
}
