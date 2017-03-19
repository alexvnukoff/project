/**
 * Created by keren on 19/03/2017.
 */

/**
 * Created by EC on 07/11/2016.
 */
// Timer setting ///////////////////////
    //Setting the ending date
    //Can be displayed as:  '31/12/2015' or 'December 31 2015' too.

    function getTimeRemaining(endtime){
        //t holds the remaining tome until end
        var t = Date.parse(endtime) - Date.parse(new Date());

        //Now converting time to usable format
        var seconds = Math.floor( (t/1000) % 60 );
        var minutes = Math.floor( (t/1000/60) % 60 );
        var hours = Math.floor( (t/(1000*60*60)) % 24 );
        var days = Math.floor( t/(1000*60*60*24) );

        //Returning data as a usable object
        return {
            'total': t,
            'days': days,
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds
        };
        //To use it and get for ex the remaining min:
        //getTimeRemaining(deadline).minutes
    }

    //Outputting the data to clockdiv
    //This function will take the id of the div which display the clock and
    //the counttime ending time.
    function initializeClock(id, endtime){
        var clock = document.getElementById(id);
        var daysSpan = clock.querySelector('.days');
        var hoursSpan = clock.querySelector('.hours');
        var minutesSpan = clock.querySelector('.minutes');
        var secondsSpan = clock.querySelector('.seconds');

        //setInterval will execute an anonymous function every second to calculate the remaining time and display it,
        //stoping when time gets to zero.
        function updateClock(){
            var t = getTimeRemaining(endtime);
            daysSpan.innerHTML = t.days;
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
