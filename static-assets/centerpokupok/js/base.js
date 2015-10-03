
function getFormat(until)
{
    now = +new Date();

    month = 60 * 60 * 24 * 30 * 1000
    day = 60 * 60 * 24 * 1000

    if(until - now >= month)
        return 'ODH'
    else if(until - now >= day)
        return 'DHM'
    else
        return 'HMS'
}

function reverseMenu(id, len){
    var menuInd = len-1;
    var reversed = Array();

    $(id+" li").each(function(){
        reversed[menuInd] = $(this);
        $(this).remove();
        menuInd--;
    });

    for (var i=0; i<len; i++){
        $(id).append($(reversed[i]));
    }
}

function convertToSheckel(isHebrew)
{
    var sheckelSym = "₪";
    var dollarSym = "$";
    var fromDollarToSheckel = 3.77;
    var fromSheckelToDollar = 0.27;

    var curSym;
    var prevSym;
    var priceMultiplier;

    if (isHebrew) {
        curSym = sheckelSym;
        prevSym = dollarSym;
        priceMultiplier = fromDollarToSheckel;

        var newPriceTop = $(".price1").text().match(/\d/g).join("")/10*3.77;
        $('.price1').text(newPriceTop+" "+sheckelSym);

        if ($('.price2')){
            var newPriceTop = $(".price2").text().match(/\d/g).join("")/10*3.77;
            $('.price2').text(newPriceTop+" "+sheckelSym);
        }
    }
    else {
        curSym = dollarSym;
        prevSym = sheckelSym;
        priceMultiplier = fromSheckelToDollar;
    }

    $('font.number').each(function(){
        var prevText = $(this).text();
        var price = prevText.match(/\d/g);
        price = price.join("");

        if (price!=0) {
            price = price / 10;
            price *= priceMultiplier;
            price = price.toFixed(2);
        }

        //var newText = prevText.replace(prevSym, curSym);
        $(this).text(price+" "+curSym);
    });
}


$(document).ready(function () {
    //langSwitch fix
    var isAr = window.location.host.indexOf('ar.');
    var isHebrew = window.location.host.indexOf('he.');

    if (isAr>=0 || isHebrew>=0) {
        $('head').append('<link id="txtalign" href="/static/centerpokupok/css/text-align.css" type="text/css" rel="stylesheet" />');
        $("select[name='country']").attr('dir', 'rtl');

        var menuLen = $("#nav-company li").length; //меню на странице продукта
        if (menuLen>0){
            reverseMenu("#nav-company", menuLen);
        }

        if (isHebrew>=0)
            convertToSheckel(true);
    }
    else {
        var alignSwitchCss = $("#txtalign");
        if (alignSwitchCss.length>0)
            $("#txtalign").remove();
        $("select[name='country']").attr('dir', 'ltr');

        var menuLen = $("#nav-company li").length; //меню на странице продукта
        if (menuLen>0){
            reverseMenu("#nav-company", menuLen);
        }
    }


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

        $(document).on('click', '#linkcart', function() {

		if ($(".cartmini").is(":hidden")){
			$(".cartmini").slideDown("fast");
		}
		else{
			$(".cartmini").slideUp("fast");
		}

		return false;
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
            var index = $(".image").index(this);
            var image = $(this).data("big");
            $('#imagebig').hide();
            $('#imagebig').fadeIn('slow');
            $('#imagebig').find('img').attr('src', image);
            $('#imagebig').find('.bzoom').data('index', index);
            return false;
        });

        $('#imagebig .bzoom').click(function() {
            var index = parseInt($(this).data('index'))
            $(".fancybox").eq(index).trigger('click');
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
    });

});
});







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

    $(".favorite").click(function(){

        if($(this).hasClass('icons'))
        {
            el = $(this)
        } else {
            el = $(this).find('i.icons')
        }

        var gid = parseInt(el.data("gid") );

        if(!gid) return false;

        var dataPost = {"ID":gid};


        if (el.hasClass('icon-heart'))
        {
             removed = "icon-heart";
             toAdd = "icon-colored-heart";
        }
        else
        {
            removed = "icon-colored-heart";
            toAdd = "icon-heart";
        }
        el.removeClass(removed);
        el.addClass("loader");



        if (gid > 0) {
            var a = $.ajax({
                type: "POST",
                url: "/products/addToFavorite/",
                data: dataPost,
                dataType: "json",
                success: function(data) {
                     el.removeClass("loader");

                     el.addClass(toAdd)


                }
            });
        }

        return false;
    });


})
