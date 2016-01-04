var device;
if( /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ) {
 device = true;
} else {device = false}

$(document).ready(function () {
	$('.checkbox').change(function(){
   	if($(this).is(':checked')) 
       $(this).parent().addClass('active'); 
	  else 
	      $(this).parent().removeClass('active')
	 });
	$('.all').change(function(){
   		if($(this).is(':checked')) 
			$('#filter li').addClass('active'); 
		else 
			$('#filter li').removeClass('active');
	 });

	$('.checkcolor').change(function(){
   	if($(this).is(':checked')) 
       $(this).parent().addClass('active'); 
	  else 
	      $(this).parent().removeClass('active')
	 });
	$('.allcolors').change(function(){
   		if($(this).is(':checked')) 
			$('#colors li').addClass('active'); 
		else 
			$('#colors li').removeClass('active');
	 });

	$(function(){
		$(".bgname").hover(function(){
		  $(this).find(".salepopup").fadeIn();
		}
	,function(){
		$(this).find(".salepopup").fadeOut();
		}
	); 
	$("#linklang").click(function(){
		$(this).attr("class","lesslang");						 
		if ($(".languagetop").is(":hidden")){
			$(".languagetop").slideDown("fast");
		}
		else{
			$(".languagetop").slideUp("fast");
			$(this).attr("class","morelang");
		}
	});
	$(document).mouseup(function(e) {
	    // Check if the click is outside the popup
	    if($(e.target).parents(".languagetop").length==0 && !$(e.target).is(".languagetop")) {
	      // Hide the popup
	      $(".languagetop").slideUp("slow");
	    }
	    if($(e.target).parents(".cartmini").length==0 && !$(e.target).is(".cartmini")) {
	      // Hide the popup
	      $(".cartmini").slideUp("slow");
	    }
	  });
	$("#linkcart").click(function(){
		if ($(".cartmini").is(":hidden")){
			$(".cartmini").slideDown("fast");
		}
		else{
			$(".cartmini").slideUp("fast");
		}
	});
	$("#sortby").click(function(){
		$(this).attr("class","lesssort");
		if ($(".sortprice").is(":hidden")){
			$(".sortprice").slideDown("fast");
		}
		else{
			$(".sortprice").slideUp("fast");
			$(this).attr("class","moresort");
		}
	});
	$(".sortprice ul li").click(function(){
		$("#sortby").html($(this).html());
	});
	$(document).mouseup(function(e) {
	    // Check if the click is outside the popup
	    if($(e.target).parents(".sortprice").length==0 && !$(e.target).is(".sortprice")) {
	      // Hide the popup
	      $(".sortprice").slideUp("slow");
	    }
	  });

	$("#linksize").click(function(){
		if ($(".allsize").is(":hidden")){
			$(".allsize").slideDown(600);
		}
		else{
			$(".allsize").slideUp(600);
		}
	});
	$(document).mouseup(function(e) {
	    // Check if the click is outside the popup
	    if($(e.target).parents(".allsize").length==0 && !$(e.target).is(".allsize")) {
	      // Hide the popup
	      $(".allsize").slideUp("slow");
	    }
	  });
	$(".allsize a").click(function(){
		$("#linksize").html($(this).html());
		$(".allsize").slideUp(300);
	});

	$(function() {
	$(".image").click(function() {
		var image = $(this).attr("rel");
	$('#imagebig').hide();
	$('#imagebig').fadeIn('slow');
	$('#imagebig').html('<img src="' + image + '"/>');
	return false;
	});

	$(".show_tips").mouseover(function(){
		$(".tip-prd").slideDown("show");
		var offset = $(this).offset();
		console.log(offset);
		$(".tip-prd").css({top:90, left:200});
	});

	$(".tip-prd").mouseenter(function(){
    }).mouseleave(function(){
    	 if ($(".tip-prd").is(":hidden")){
 			$(".tip-prd").slideDown("show");
 		}
 		else{
 			$(".tip-prd").slideUp("show");
 		}
    });

});
});



if (device) {
		$("#sidevar li.level1-li").click(function(){
			$(this).children().toggleClass('active');
			$(this).siblings().children().removeClass('active');
			$(this).toggleClass('active');
		});
		$("#sidevar li.level1-li").hover(function() {
		  $(this).children('.listHolder').css('left', '-9999px');
		  $(this).children('a').css({'background-color': 'transparent', 'color': '#4b8ab6', 'padding-left': '0'});
		});
};

function googleMap_initialize() {
  var lat = $('#map-canvas').attr('lat');
  var long = $('#map-canvas').attr('long');
  var mapCenterCoord = new google.maps.LatLng(lat, long);
  var mapMarkerCoord = new google.maps.LatLng(lat, long);

  var mapOptions = {
    center: mapCenterCoord,
    zoom: 17,
    //draggable: false,
    disableDefaultUI: true,
    scrollwheel: false,
    mapTypeId: google.maps.MapTypeId.ROADMAP
  };

  var map = new google.maps.Map(document.getElementById('map-canvas'), mapOptions);
  var marker = new google.maps.Marker({
    position: mapMarkerCoord, 
    map: map
  });
  $(window).resize(function (){
    map.setCenter(mapCenterCoord);
  });
};

	if ($('#map-canvas').length > 0) {
		googleMap_initialize();
	};


})