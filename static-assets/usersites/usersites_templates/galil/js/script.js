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
	$('a[href="' + this.location.pathname + '"]').parents('li').addClass('active');

	//resizing iframes video to make it responsive
	//--------------------------------------------
	// Find all iframes
	var $iframes = $( "iframe" );

	// Find &#x26; save the aspect ratio for all iframes
	$iframes.each(function () {
	  $( this ).data( "ratio", this.height / this.width )
		// Remove the hardcoded width &#x26; height attributes
		.removeAttr( "width" )
		.removeAttr( "height" );
	});

	// Resize the iframes when the window is resized
	$( window ).resize( function () {
	  $iframes.each( function() {
		// Get the parent container&#x27;s width
		var width = $( this ).parent().width();
		$( this ).width( width )
		  .height( width * $( this ).data( "ratio" ) );
	  });
	// Resize to fix all iframes on page load.
	}).resize();

});