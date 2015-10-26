/*
#############################
#   Main JS for ____________   #
#############################
*/

$(document).on('click', '.sub', function(event){
  event.preventDefault();
})

$(document).ready(function() {

$('.sidebar-menu>li').each(function(){
    var hrefNum = $(this).children().length;
    if (hrefNum == 1) {
      $(this).children().css('background-image', 'none');
    }
  })

 $(function() { // sidebar menu toggle
    $(".sidebar-menu>li>a").click(function(event) {
        if ($(this).siblings().size() > 0) {
          event.preventDefault();
        }

        $(this).toggleClass('active').next(".sidebar-menu__submenu").slideToggle(400) /*opens the child submenu*/
        .parent().siblings().children('.sidebar-menu__submenu:visible').css('display', 'none'); /*closes any opened ones*/
        $(this).parent().siblings().children().removeClass('active');
    });
  });

  $(function() { // icons vertical align
      $("#display-vertical").click(function(event) {
          event.preventDefault();
          if ($(window).width() > 1000) {
            $('body').toggleClass('display-vertical');
            if ($('body').hasClass('display-vertical')){
              $(this).text('horizontal');
            } else {
              $(this).text('vertical');
            }
          };   
        });
    });


  $(function() { // icons after sidebar menu
    if ($(window).width() < 700) {
      $('.offer__icons').clone().insertAfter('.sidebar-menu');
    }
  });

  $(function(){
    $(window).resize(function(event) {
      if ($(window).width() <= 1000) {
        $('body').removeClass('display-vertical');
      };
    });
  })


  $(function() { // main menu mobile
      $("#menuToggle").click(function() {
          $('.horMenu').slideToggle(400);
      });
    });

  $(function() {
      $(".select").click(function() {
        $(this).find('.select-dropdown').slideToggle('fast');
      });
    });

  $(function(){
    var date = $('#timer').attr('date');
    $('.timer').countdown({until: new Date(date), format: 'dHM'});
  })

  $(function(){
    var date = $('.timer-mini').attr('date');
    $('.timer-mini').countdown({until: new Date(date), compact: true});
  })
  

  //--------------------------------Google Карта в футере ---------------------------------
  function googleMap_initialize() {

      $.getJSON( "settings.json").done(function(data){
        var mapCenterCoord = new google.maps.LatLng(data.map.lat, data.map.longt);
        var mapMarkerCoord = new google.maps.LatLng(data.map.lat, data.map.longt);

        var mapOptions = {
          center: mapCenterCoord,
          zoom: 13,
          //draggable: false,
          disableDefaultUI: true,
          scrollwheel: false,
          mapTypeId: google.maps.MapTypeId.ROADMAP
        };

        var map = new google.maps.Map(document.getElementById('map'), mapOptions);

        var markerImage = new google.maps.MarkerImage('images/svg/marker.svg');
        var marker = new google.maps.Marker({
          icon: markerImage,
          position: mapMarkerCoord, 
          map: map,
          title:"Omega Tours"
        });

        $(window).resize(function (){
          map.setCenter(mapCenterCoord);
        });  
      }) 

  };
  googleMap_initialize();


  $('.-lang .select-dropdown a').on('click', function(event) {
    event.preventDefault();
    $('body').removeClass('hebrew');
    var currentLang = $(this).text();
    $('.select.-lang>span').text(currentLang);
  });


$('.-lang .lang-hebrew').on('click', function(event) {
    event.preventDefault();
    $('body').addClass('hebrew');
  });


/*------------------ Sending forms -----------------------*/
/*--------------------------------------------------------*/
/*--------------------------------------------------------*/
  function validateEmail(email) {
      var re = /^([\w-]+(?:\.[\w-]+)*)@((?:[\w-]+\.)*\w[\w-]{0,66})\.([a-z]{2,6}(?:\.[a-z]{2})?)$/i;
      return re.test(email);
  }

  $(function(){
    $('input').add('textarea').on('focusin', function(event) {
      $(this).removeClass('error');
    });
  })

// обработчик форм
  $('form').on('submit', function(event) {
    event.preventDefault();

    var data = $(this).serialize();
    console.log(data);
    $.ajax({
      type: 'POST',
      url: 'forms.php',
      data: data,
      success: function(result){
        if (result.status == 'ok') {
            $('a.popup-modal').click();
        } else {
          alert(result);
        }
        $('form').each(function(){
          $(this)[0].reset();
        });
      },
      error: function(result) {
        alert(result);
      }
    });

  });

});