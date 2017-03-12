jQuery(document).ready(function($) {
  $('#media').carousel({
    pause: true,
    interval: false,
  });

   // $("div.bhoechie-tab-menu>div.list-group>a").hovclicker(function(e) {
   //      e.preventDefault();
   //      $(this).siblings('a.active').removeClass("active");
   //      $(this).addClass("active");
   //      var index = $(this).index();
   //      $("div.bhoechie-tab>div.bhoechie-tab-content").removeClass("active");
   //      $("div.bhoechie-tab>div.bhoechie-tab-content").eq(index).addClass("active");
   //  });
   // $("div.bhoechie-tab-menu>div.list-group>a").mouseout(function(e) {
   //      e.preventDefault();
   //      $(this).siblings('a.active').removeClass("active");
   //      $(this).removeClass("active");
   //  });

   $('#media').carousel({
    pause: true,
    interval: false,
  });

   $("#owl-slide-1").owlCarousel({
 
      //autoPlay: 3000, //Set AutoPlay to 3 seconds
 
      items : 4,
      itemsDesktop : [1199,3],
      itemsDesktopSmall : [979,3]
 
  });

   $("#owl-slide-2").owlCarousel({
 
      //autoPlay: 3000, //Set AutoPlay to 3 seconds
 
      items : 4,
      itemsDesktop : [1199,3],
      itemsDesktopSmall : [979,3]
 
  });

   //products carusel
   $('#product_carousel').on('slide.bs.carousel', function (evt) {
      $('#product_carousel .controls li.active').removeClass('active');
      $('#product_carousel .controls li:eq('+$(evt.relatedTarget).index()+')').addClass('active');
    })

   //company page inner navigation
   $('#comp-nav').children('li').first().children('a').addClass('active')
        .next().addClass('is-open').show();

    if ($(document).width() <= 480){
    	$('#comp-nav').children('li').first().children('a').removeClass('active')
        .next().removeClass('is-open').hide();
    }    
        
    $('#comp-nav').on('click', 'li > a', function() {
      console.log("$('#comp-nav').height()");
      console.log($('#comp-nav').height());

      if (!$(this).hasClass('active')) {

        $('#comp-nav .is-open').removeClass('is-open').hide();
        $(this).next().toggleClass('is-open').toggle();
          
        $('#comp-nav').find('.active').removeClass('active');
        $(this).addClass('active');
      } else if ($(document).width() <= 480){
        $('#comp-nav .is-open').removeClass('is-open').hide();
        $(this).removeClass('active');
      }
   });

    //prevent the tab empty link from jumping to the top
    $('a.empty-link').click(function(e)
	{
	    // Cancel the default action
	    e.preventDefault();
	});
});


