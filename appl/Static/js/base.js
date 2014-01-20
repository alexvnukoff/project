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

    $(function () {
        bigCoupon = $('#topCountdown');

        if(bigCoupon.length > 0)
        {
            var until = parseInt(bigCoupon.data('countdown')) * 1000;
            bigCoupon.countdown({until: new Date(until), format: getFormat(until)})
        }
    })

})