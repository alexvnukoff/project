$(document).ready(function() {

var path = (window.location.host).split('.');
path = path[0];

if (document.getElementsByClassName('currency_symbol').length > 0) {
var currency = document.getElementsByClassName('currency_symbol')[0];
$('.currency_for_total_cost').html(currency.innerHTML);

}

$("#lang_select").find('option').each(function( i, opt ) {
    if( opt.value === path )
        $(opt).attr('selected', 'selected');
});

$('.category-selector').on('change', function() {
    window.location.href = this.value
});

$("#item-amount").keyup(function() {
    document.getElementById('id_quantity').value = this.value;
});

$("#lang_select" ).change(function(e) {
    if(!$(this).val())
        return;

    var languages = ["am","ar","en","he","ru","zh"];

    if ($.inArray(path[0], languages) > -1) {
        path[0] = $(this).val();
    }
});

$( "#lang_select" ).change(function(e) {
    if (!$( this ).val())
        return;

    path = (window.location.host).split('.');

    if (path[0] == 'www'){
        delete path[0]
    }

    var languages = ["am", "ar", "en", "he", "ru", "zh"];
    if($.inArray(path[0], languages)>-1){
        path[0] = $(this).val();
    }

    window.location.href = window.location.protocol + "//" + path.join('.');
});

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
        .parent().siblings().children('.sidebar-menu__submenu:visible').slideToggle(400); /*closes any opened ones*/
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


/*  $(function() { // icons after sidebar menu
    if ($(window).width() < 700) {
      $('.offer__icons').clone().insertAfter('.sidebar-menu');
    }
  });
*/
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

  $('.offer__slider').slick({
    dots: true,
    arrows: false,
    fade: true,
    autoplay: true,
    speed: 1000
  });

if ( $(".InfoTabs").length > 0 ) {
    $( ".InfoTabs" ).tabs();
  };

if ($('.fancybox').length > 0) {
    $('.fancybox').fancybox({
      centerOnScroll: true,
     helpers: {
    overlay: {
      locked: false
    }
  }
    });
  };

  $(function(){
    var date = $('.timer').attr('date');
    $('.timer').countdown({until: new Date(date), format: 'dHM'});
  })

  $(function(){
    var date = $('.timer-mini').attr('date');
    $('.timer-mini').countdown({until: new Date(date), compact: true});
  })

  $('.display-list').on('click', function() {
    $(this).addClass('active');
    $(this).siblings('button').removeClass('active');
    $('.content__info').removeClass('grid-layout');
    $('.content__info').addClass('layout');
  });

  $('.display-square').on('click', function() {
    $(this).addClass('active');
    $(this).siblings('button').removeClass('active');
    $('.content__info').removeClass('layout');
    $('.content__info').addClass('grid-layout');

  });
});

$('.select-dropdown a').on('click', function(event) {
    event.preventDefault();
    $('body').removeClass('hebrew');
    var currentLang = $(this).text();
    $('.select.-lang>span').text(currentLang);
  });


$('.lang-hebrew').on('click', function(event) {
    event.preventDefault();
    $('body').addClass('hebrew');
  });

Share = {
        vkontakte: function(purl, ptitle, pimg, text) {
            var url  = 'http://vkontakte.ru/share.php?';
            url += 'url='          + encodeURIComponent(purl);
            url += '&title='       + encodeURIComponent(ptitle);
            url += '&description=' + encodeURIComponent(text);
            url += '&image='       + encodeURIComponent(pimg);
            url += '&noparse=true';
            Share.popup(url);
        },
        odnoklassniki: function(purl, text) {
            var url  = 'http://www.odnoklassniki.ru/dk?st.cmd=addShare&st.s=1';
            url += '&st.comments=' + encodeURIComponent(text);
            url += '&st._surl='    + encodeURIComponent(purl);
            Share.popup(url);
        },
        facebook: function(purl, ptitle, pimg, text) {
            var url  = 'http://www.facebook.com/sharer.php?s=100';
            url += '&p[title]='     + encodeURIComponent(ptitle);
            url += '&p[summary]='   + encodeURIComponent(text);
            url += '&p[url]='       + encodeURIComponent(purl);
            url += '&p[images][0]=' + encodeURIComponent(pimg);
            Share.popup(url);
        },
        twitter: function(purl, ptitle) {
            var url  = 'http://twitter.com/share?';
            url += 'text='      + encodeURIComponent(ptitle);
            url += '&url='      + encodeURIComponent(purl);
            url += '&counturl=' + encodeURIComponent(purl);
            Share.popup(url);
        },
        mailru: function(purl, ptitle, pimg, text) {
            var url  = 'http://connect.mail.ru/share?';
            url += 'url='          + encodeURIComponent(purl);
            url += '&title='       + encodeURIComponent(ptitle);
            url += '&description=' + encodeURIComponent(text);
            url += '&imageurl='    + encodeURIComponent(pimg);
            Share.popup(url)
        },

        me : function(el){
            console.log(el.href);
            Share.popup(el.href);
            return false;
        },
        popup: function(url) {
            window.open(url,'','toolbar=0,status=0,width=626,height=436');
        }
};