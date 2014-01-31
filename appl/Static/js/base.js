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

tip = $('#jcart-tooltip');


    // Tooltip is added to the DOM on mouseenter, but displayed only after a successful Ajax request
$('.bigbuy').mouseenter(
   function(e) {
     var x = e.pageY + 25,
     y = e.pageX + -10;
     $('body').append(tip);
         tip.css({top: y + 'px', left: x + 'px'});
     }
)
.mousemove(
    function(e) {
            var y = e.pageY + 25,
                x = e.pageX + -10;
            tip.css({top: y + 'px', left: x + 'px'});
    }
)
.mouseleave(
        function() {
            tip.hide();
        }
    );

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

// добавление в корзину на ajax
    $(".bigbuyn").click(function(){
        var gid = parseInt( $(this).data("gid") );

        if(!gid) return false;

        var count = $('input[name="french-hens"]').val();
        var dataPost = {"ID":gid, "count":count };

        $(this).fadeTo(10, 0.5);

        $button = $(this);

        function callback_add(data, textStatus)
        {
            if (!data["BASKET_OUTPUT"] || !data["RESULT"] || !data["RESULT"]["TYPE"] || !data["RESULT"]["MESS"])
            {
				
                tip.text(data["RESULT"]["MESS"]);

            } else {
                if (data["RESULT"]["TYPE"] == "OK") {
                    if( $.trim(data["BASKET_OUTPUT"]) != "" )
                    {
                        $("#basket_line_block").replaceWith( data["BASKET_OUTPUT"] );

                    }
                    tip.text('Товар добавлен в корзину');
                    updateBasket();
                } else {
                    tip.text(data["RESULT"]["MESS"]) ;
                }
            }



            $button.fadeTo(0, 1);
            tip.fadeIn('100').delay('700').fadeOut('100');

            window.setTimeout(function(){
                $(".to_delete", $(this).parent()).remove();
            }, 1500);
        };

        if (gid > 0) {
            var a = $.ajax({
                type: "POST",
                url: "/products/basket/addtobasket/",
                data: dataPost,
                dataType: "json",
                success: callback_add
            });
        }

        return false;
    });






    $(document).on('click','.inc',function(){
            var item = $(this).parents("li.product_id");

            var pricePerOne = parseFloat(item.find("font.number").text());

            var quantity = parseFloat(item.find("input#french-hens").val());

            var price = pricePerOne*quantity;
            item.find("input#french-hens").val(quantity);
            item.find("div.price").text(price);
            var allprice = pricePerOne + parseFloat($("input.sumMoney").val());

            $("input.sumMoney").val(allprice);
            allprice = allprice.toFixed(2).replace('.',',').replace(/(\d)(?=(\d{3})+\,)/g,"$1 ");
            $("span.right.sumMoney strong").text(allprice);


            var gid = parseInt(item.data("gid"))
            var dataPost = {"ID":gid, "count":quantity};
            var a =  $.ajax({
                type: "POST",
                url: "/bitrix/templates/b2c/ajax_php/cart.php",
                data: dataPost,
                dataType: "json",
                success: callback

            });

        }
    );


    $(document).on('click','.dec',function(){
            var item = $(this).parents("li.product_id");

            var pricePerOne = parseFloat(item.find("font.number").text());

            var quantity = parseFloat(item.find("input#french-hens").val());
            if (quantity == 0)
            {
                item.find("input#french-hens").val(0);
                item.find("div.price").text(0);
                $("span.right.sumMoney strong ").text(0);
                $("input.sumMoney").val(0)
                deleteElement(item);
                return;

            }




            var price = pricePerOne*quantity;
            item.find("input#french-hens").val(quantity);
            item.find("div.price").text(price);
            var allprice =parseFloat($("input.sumMoney").val()) - pricePerOne  ;

            $("input.sumMoney").val(allprice);
            allprice = allprice.toFixed(2).replace('.',',').replace(/(\d)(?=(\d{3})+\,)/g,"$1 ");
            $("span.right.sumMoney strong ").text(allprice);

            var gid = parseInt(item.data("gid"));
            var dataPost = {"ID":gid, "count":quantity};
            $.ajax({
                type: "POST",
                url: "/bitrix/templates/b2c/ajax_php/cart.php",
                data: dataPost,
                dataType: "json",
                success: callback
            });

        }
    );


    $(document).on('click', ".icons.i-delete",function() { deleteElement($(this).parents("li.product_id")) });
        function  deleteElement(item) {

            var money =  parseFloat(item.find("div.price").text());
            var allprice =parseFloat($("input.sumMoney").val()) - money  ;
            if(allprice==0)
            {
                $("li.total").remove();
                $("ul#itemcart").html("<span style='color: red'>Корзина пуста</span>");
            }

            $("input.sumMoney").val(allprice);
            allprice = allprice.toFixed(2).replace('.',',').replace(/(\d)(?=(\d{3})+\,)/g,"$1 ");
            $("span.right.sumMoney strong ").text(allprice);


            var gid = parseInt(item.data("gid"));
            var dataPost = {"ID":gid, "count":0};
            $.ajax({
                type: "POST",
                url: "/bitrix/templates/b2c/ajax_php/cart.php",
                data: dataPost,
                dataType: "json",
                success: callback
            });


           item.remove();
			updateBasket();
			
           

            return false;

    }
    function callback(data, textStatus)
    {
      

        if (!data["BASKET_OUTPUT"] || !data["RESULT"] || !data["RESULT"]["TYPE"] || !data["RESULT"]["MESS"])
        {
            tip.text('Ошибка добавления в корзину');

        } else {
            if (data["RESULT"]["TYPE"] == "OK") {
                if( $.trim(data["BASKET_OUTPUT"]) != "" )
                {
                    $("#basket_line_block").empty().html( data["BASKET_OUTPUT"] );
                }

            } else {
                tip.text(data["RESULT"]["MESS"]) ;
            }
        }

    };


});



////////


function updateBasket()
{
    $.ajax({
        url: "/ajax.handler.php",
        type: "POST",
        dataType: "html",
        data: "PAGE=BASKET",
        success: function(data){
            $('.cartmini').empty();
            $('.cartmini').html(data)
        }
    });

}