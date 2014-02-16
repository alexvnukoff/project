$(document).ready(function() {
       socket_connect();

        function socket_connect() {
            socket = new SockJS('http://' + window.location.host + ':9999/orders');  // ваш порт для асинхронного сервиса
            // при соединении вызываем событие login, которое будет выполнено на серверной стороне

            socket.onmessage = function(msg){
                var data = msg['data']
                var type = JSON.parse(data).type
                if (type == 'notification')
                {
                    el = $(document).find(".imgnews.i-note")
                    num = el.siblings(".num").text()
                    if (num)
                    {
                        el.siblings(".num").text(parseInt(num)+1)
                    }
                    else
                    {
                        el.siblings(".num").text(1)
                    }


                }
                console.log(el)


            }

            socket.onclose = function(e){
                setTimeout(socket_connect, 5000);
            };
        }



function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;

            }
        }
    }
    return cookieValue;
}

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
             var csrftoken = getCookie('csrftoken');
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

    $("#country").click(function(){
		if($(".country-list").is(":hidden")){
			$(".country-list").slideDown(100);
		}
		else{
			$(".country-list").slideUp(100);
		}
	});
	$(document).mouseup(function(e) {
	    // Check if the click is outside the popup
	    if($(e.target).parents(".country-list").length==0 && !$(e.target).is(".country-list")) {
	      // Hide the popup
	      $(".country-list").slideUp(100);
	    }
	  });
	$(".country-list ul li a").click(function(){
		$(".textfilter").html($(this).html());
		$(".country-list").slideUp(100);
	});
	//Type droplist
	$("#type").click(function(){
		if($(".type-list").is(":hidden")){
			$(".type-list").slideDown(100);
		}
		else{
			$(".type-list").slideUp(100);
		}
	});
	$(document).mouseup(function(e) {
		if($(e.target).parents(".type-list").length==0 && !$(e.target).is(".type-list")) {
		  $(".type-list").slideUp(100);
		}
	});
	$("#part").click(function(){
		if($(".part-list").is(":hidden")){
			$(".part-list").slideDown(100);
		}
		else{
			$(".part-list").slideUp(100);
		}
	});
	$(document).mouseup(function(e) {
		if($(e.target).parents(".part-list").length==0 && !$(e.target).is(".part-list")) {
		  $(".part-list").slideUp(100);
		}
	});
	$(".part-list ul li a").click(function(){
		$(".textpart").html($(this).html());
		$(".part-list").slideUp(100);
	});
	$("i.i-close").click(function(){
		$(this).parent().parent().hide();
	});
	
	$(".select-all1").click(function(){
		$(".type1 input[type='checkbox']").prop("checked", $(this).is(":checked"));
	});
	$(".select-all2").click(function(){
		$(".type2 input[type='checkbox']").prop("checked", $(this).is(":checked"));
	});
	$(".btntype1").click(function(){
		$(".type-list input[type='checkbox']").prop("checked", $(this).is(":checked"));
	});
	$(".btntype2").click(function(){
		$(".type-list").slideUp(100);
	});
	
	$("#showevent").click(function(){
        el = $(document).find(".imgnews.i-note")
        num = el.siblings(".num").text()
		if($(".formevent").is(":hidden") && parseInt(num)>0){
            var  el = $(".formevent")
			el.show();
            el.find('#not-content').empty()
            el.find('#load').show()
             var a = $.ajax({
                type: "POST",
                url: "/notification/get/",
                data: "",
                dataType: "html",
                success: function(data) {
                     el.find('#load').hide()

                     el.find('#not-content').append(data)



                }
            });





		}
		else{
			$(".formevent").hide();


		}
	});
	$(".close-event").click(function(){
		$(".formevent").hide();
	});
	$("#filter-link").click(function(){
		$(".filter-form, #fade-profile").show();
	});
	$(".close-event").click(function(){
		$(".filter-form, #fade-profile").hide();
	});
	$(".btnprofile").click(function(){
		if($("#light-profile, #fade-profile").is(":hidden")){
			$("#light-profile, #fade-profile").show();
		}
		else{
			$("#light-profile, #fade-profile").hide();
		}
	});
});