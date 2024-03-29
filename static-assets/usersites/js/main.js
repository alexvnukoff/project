$(document).ready(function() {

if (document.getElementsByClassName('currency_symbol').length > 0) {
var currency = document.getElementsByClassName('currency_symbol')[0];
$('.currency_for_total_cost').html(currency.innerHTML);
}

$('.category-selector').on('change', function() {
    window.location.href = this.value
});

$("#id_quantity_src").keyup(function() {
    document.getElementById('id_quantity').value = this.value;
});

var langs = []

if($("#id_amount_src").get(0)) {
  if($("#id_amount").get(0)) {
    document.getElementById('id_amount').value = document.getElementById('id_amount_src').value;
  };
};

$(document).ready(function() {
    var path = (window.location.host).split('.');
    path = path[0];
    $("#lang_select").find('option').each(function( i, opt ) {
        langs.push(opt.value);

        if( opt.value === path ) {
            $(opt).attr('selected', 'selected');
        }
    });
});

$( "#lang_select" ).change(function(e) {
    if (!$( this ).val())
      return;

    path = (window.location.host).split('.');
    if (path[0] == 'www'){
        path[0] = $( this ).val();
    } else if ($.inArray(path[0], langs) > -1) {
        path[0] = $( this ).val()
    } else {
        path.unshift($( this ).val())
    }

    host = path.join('.');

    window.location.href =window.location.protocol + "//" + host  +
            window.location.pathname + window.location.search + window.location.hash;

});


if($('.offer__icons').children().length < 1) {
      $('.offer__icons').hide();
  }

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
  });

  $(function(){
    var date = $('.timer-mini').attr('date');
    $('.timer-mini').countdown({until: new Date(date), compact: true});
  });

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

if($("display-vertical").get(0)) {
$(function(){
    $(window).resize(function(event) {
      if ($(window).width() <= 1000) {
        $('body').removeClass('display-vertical');
      } else {$('body').addClass('display-vertical');};
    });
    if ($(window).width() < 1000) {
       $('body').removeClass('display-vertical');
    }
      else { $('body').addClass('display-vertical'); }

  });
};


// The dialog forms
var DIALOG_FORM_OPEN_CLS = '.dialog-open',
    DIALOG_FORM_CLS = '.dialog-form',
    DIALOG_HREF_CLS = '.dialog-href';

$(document).ready(function() {
    // The search with autocomplete
    if (typeof SEARCH_Q_URL !== 'undefined') {
        var search_cache = {};
        $('#search_q').autocomplete({
            minLength: 2,
            source: function(request, response) {
                var term = request.term;
                if (term in search_cache) {
                    response(search_cache[term]);
                    return;
                }
                $.getJSON(SEARCH_Q_URL, request, function(data, status, xhr) {
                    search_cache[term] = data;
                    response(data);
                });
            }
        }).data('ui-autocomplete')._renderItem = function(ul, item) {
            return $('<li></li>')
                .data('item.autocomplete', item)
                .append('<img style="margin: 5px; height="20" src="' + item.img + '" />')
                .append(item.label)
                .appendTo(ul);
        };
    }

    $(DIALOG_FORM_OPEN_CLS).on('click', function(e) {
        e.preventDefault();
        $('#navbarCollapse').collapse('hide');
        processDialogForm(this);
    });
    
});    


var processDataDialogDivId = 'processDataDialog',
    processDataDialogId = '#' + processDataDialogDivId;

/**
 * Process the dialog form for clicked 'href'
 */
function processDialogForm(selectedHref) {
    var url = $(selectedHref).attr('href'),
        processDataDialog = $(processDataDialogId);
    if (processDataDialog.length == 0) {
        var processDataDialog = $('<div/>')
            .attr('height', 300)
            .attr('id', processDataDialogDivId)
            .hide();
        $('body').children(':first').prepend(processDataDialog);
    }
    $(processDataDialog).dialog({
        autoOpen: false,
        minHeight: 300,
        minWidth: 200,
        maxWidth: 400,
        width: 300,
        modal: true,
        draggable: true,
        resizable: true,
        open: function() {
            initDialogForms();
            initDialogHrefs();
        }
    });
    
    $.get(url, function(data) {
        var title = $(selectedHref).data('title') || 'User registration';
        $(processDataDialog).dialog('option', 'title', title);
        $(processDataDialog).html(data).dialog('open');
        $(processDataDialog).dialog("widget").css('height', 'auto');
    });
}

/**
 * Assign the handler for form submitting
 */
function initDialogForms() {
    $(DIALOG_FORM_CLS).each(function() {
        $(this).submit(function(event) {
            event.preventDefault();
            $(this).ajaxSubmit({
                success: function(data, textStatus, jqXHR) {
                    var newFormDiv,
                        newContent = $.parseHTML(data),
                        newDiv = $.grep(newContent, function(item) {
                            return $(item).is('div');
                        }),
                        checkMeta = $.grep(newContent, function(item) {
                            return $(item).is('meta');
                        });
                    if (checkMeta.length > 0) {
                        $(processDataDialogId).dialog('close');                    
                        location.reload();
                    } else if ((newDiv.length > 0) && $(processDataDialogId).dialog('isOpen')) {
                        newFormDiv = $(newDiv).children(':first');
                        $(DIALOG_FORM_CLS).each(function() {
                            $(this).remove();
                        });
                        $('#main_wrapper').empty().append(newFormDiv);
                        initDialogForms();
                        initDialogHrefs();
                    }
                },
                error: function(jqXHR, testStatus) {
                    $(processDataDialogId).dialog('close');                    
                }
            });
        });
    });
}


/**
 * Assign the handler for hrefs in dialogs
 */
function initDialogHrefs() {
    $(DIALOG_HREF_CLS).each(function() {
        $(this).click(function(event) {
            event.preventDefault();
            var url = $(this).attr('href');
            $.get(url, function(data) {
                var newFormDiv,
                    newContent = $.parseHTML(data),
                    newDiv = $.grep(newContent, function(item) {
                        return $(item).is('div');
                    });
                if ((newDiv.length > 0) && $(processDataDialogId).dialog('isOpen')) {
                    newFormDiv = $(newDiv).children(':first');
                    $(DIALOG_FORM_CLS).each(function() {
                        $(this).remove();
                    });
                    $('#main_wrapper').empty().append(newFormDiv);
                    initDialogForms();
                    initDialogHrefs();
                 }
            });
        });
    });
}


