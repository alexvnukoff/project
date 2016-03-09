


$(document).ready( function() {
	//$('.main-navbar .navbar-nav li').first().addClass('active');

    $('#myCarousel').carousel({
		interval: 4000,
	}).trigger('slid');

	var clickEvent = false;

	$('#myCarousel').on('click', '.nav li', function() {
			clickEvent = true;
			$('.nav li').removeClass('active');
			$(this).parent().addClass('active');
	}).on('slid.bs.carousel', function(e) {
		if(!clickEvent) {
			var count = $('.carousel-text .nav').children().length -1;
			var current = $('.carousel-text .nav li.active');
			current.removeClass('active').next().addClass('active');
			var id = parseInt(current.data('slide-to'));
			if(count == id) {
				$('.carousel-text .nav li').first().addClass('active');
			}
		}
		clickEvent = false;
	});

	//Attach events to menu
  $('.main-navbar .navbar-nav li').on('click', function(e){
	  //e.preventDefault();
	  //$('li').removeClass('active');
	  //$(this).addClass('active');
	  //var siblings =($(this).siblings());
      //
	  ////Remove active class on all buttons
	  //siblings.each(function (){
		//  $(this).removeClass('active');
		//})
      //
      //
	  ////Add the clicked button class
	  //$(this).addClass('active');


	//$(".navbar-nav li").click(make_button_active);
  });

});