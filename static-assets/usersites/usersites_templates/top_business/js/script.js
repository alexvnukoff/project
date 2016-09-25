$('.gallery__thumbnail').click(function(){
  	$('.modal-body').empty();
  	var title = $(this).parent('a').attr("title");
  	$('.modal-title').html(title);
  	$($(this).parents('div').html()).appendTo('.modal-body');
  	$('#myModal').modal({show:true});
});

jQuery(document).ready(function($) {
 
    $('#galCarousel').carousel({
            interval: 5000
    });
 
        //Handles the carousel thumbnails
    $('[id^=carousel-selector-]').click(function () {
        var id_selector = $(this).attr("id");
        try {
            var id = /-(\d+)$/.exec(id_selector)[1];
            console.log(id_selector, id);
            jQuery('#galCarousel').carousel(parseInt(id));
        } catch (e) {
            console.log('Regex failed!', e);
        }
    });

    // When the carousel slides, auto update the text
    $('#galCarousel').on('slid.bs.carousel', function (e) {
             var id = $('.item.active').data('slide-number');
            $('#caracebookousel-text').html($('#slide-content-'+id).html());
    });

    // Media carusel
    $('#media').carousel({
	    pause: true,
	    interval: false,
	  });

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

	//menu active
	$('.navbar-nav>li>a').click(function(){
		$('.navbar-nav li.active').removeClass('active');
		$(this).parent().addClass('active');
	});
});

//jQuery(window).load(function() {
//   setFooterStick();
//});

//getting the height of the footer, make the margin-bottom of the body as the height of the footer.
(function setFooterStick(){
	var footerHeight = $('footer').height()+100;
	var heightStr = footerHeight + "px";
	$('body').css("margin-bottom", heightStr);
	//document.body.style.marginBottom = heightStr;
})();