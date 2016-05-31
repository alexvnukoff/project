function getTimeRemaining(endtime){
	/* t - holds the remqining time until end time. The parse will give the time in miliseconds, which will give us the option to substruct */
	var t = Date.parse(endtime) - Date.parse(new Date());

	/* Convering the time to usable format */
	var seconds = Math.floor( (t/1000) % 60 );
	var minutes = Math.floor( (t/1000/60) % 60 );
	var hours = Math.floor( (t/(1000*60*60)) % 24 );
	var days = Math.floor( t/(1000*60*60*24) );

	return {
		'total': t,
		'days': days,
		'hours': hours,
		'minutes': minutes,
		'seconds': seconds
	};
}

function initializeClock(id, endtime){
	/* Saving the clock element id  for further use */
	var clock = document.getElementById(id);
	var daysSpan = clock.querySelector('.days');
	var hoursSpan = clock.querySelector('.hours');
	var minutesSpan = clock.querySelector('.minutes');
	var secondsSpan = clock.querySelector('.seconds');

	/* An anonymus function to:
		calculate the remining time.
		Output the remaining time.
		Stop where it gets to zero. */
	function updateClock(){
		var t = getTimeRemaining(endtime);

		daysSpan.innerHTML = ('0' + t.days).slice(-2);
		hoursSpan.innerHTML = ('0' + t.hours).slice(-2);
		minutesSpan.innerHTML = ('0' + t.minutes).slice(-2);
		secondsSpan.innerHTML = ('0' + t.seconds).slice(-2);
	  	if(t.total<=0){
	    	clearInterval(timeinterval);
	  	}
	}

	updateClock(); // run function once at first to avoid delay
	var timeinterval = setInterval(updateClock,1000);
}

var deadline = new Date(Date.parse(new Date()) + 15 * 24 * 60 * 60 * 1000);
initializeClock('clockdiv', deadline);