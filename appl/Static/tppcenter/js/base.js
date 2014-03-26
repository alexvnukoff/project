function updateURLParameter(param, paramVal, url)
{
    if (!url) url = window.location.href;
    var TheAnchor = null;
    var newAdditionalURL = "";
    var tempArray = url.split("?");
    var baseURL = tempArray[0];
    var additionalURL = tempArray[1];
    var temp = "";

    if (additionalURL)
    {
        var tmpAnchor = additionalURL.split("#");
        var TheParams = tmpAnchor[0];
            TheAnchor = tmpAnchor[1];
        if(TheAnchor)
            additionalURL = TheParams;

        tempArray = additionalURL.split("&");

        for (i=0; i<tempArray.length; i++)
        {
            if(tempArray[i].split('=')[0] != param)
            {
                newAdditionalURL += temp + tempArray[i];
                temp = "&";
            }
        }
    }
    else
    {
        var tmpAnchor = baseURL.split("#");
        var TheParams = tmpAnchor[0];
            TheAnchor  = tmpAnchor[1];

        if(TheParams)
            baseURL = TheParams;
    }

    if(TheAnchor)
        paramVal += "#" + TheAnchor;

    var rows_txt = temp + "" + param + "=" + paramVal;
    return baseURL + "?" + newAdditionalURL + rows_txt;
}


$(document).ready(function() {

        $(document).on("click", ".buttonremove", function() {
            $(this).parents(".addpage-form").remove();
            var formin = $('.append-formin');
            var num =  parseInt(formin.find("#count").val())-1;
            formin.find("#count").val(num);
            return false
        });

        $("#country").click(function(){
            if($(".country-list").is(":hidden")){
                $(".country-list").slideDown(100);
            }
            else{
                $(".country-list").slideUp(100);
            }
        });

        $(".deleteimge").click(function(){
                $(this).parent().find(".gray-img").show();
                $(this).parent().find("#delete").attr('checked', 'checked');

            });

        $(document).mouseup(function(e) {
            // Check if the click is outside the popup
            if($(e.target).parents(".country-list").length==0 && !$(e.target).is(".country-list")) {
              // Hide the popup
              $(".country-list").slideUp(100);
            }
          });

        $(".country-list ul li a").click(function(){
            $(".textfilter").html($(this).html());
            $(".country-list").slideUp(100);
        });

        //Type droplist
        $("#type").click(function(){
            if($(".type-list").is(":hidden")){
                $(".type-list").slideDown(100);
            }
            else{
                $(".type-list").slideUp(100);
            }
        });
        $(document).mouseup(function(e) {
            if($(e.target).parents(".type-list").length==0 && !$(e.target).is(".type-list")) {
              $(".type-list").slideUp(100);
            }
        });
        $("#part").click(function(){
            if($(".part-list").is(":hidden")){
                $(".part-list").slideDown(100);
            }
            else{
                $(".part-list").slideUp(100);
            }
        });
        $(document).mouseup(function(e) {
            if($(e.target).parents(".part-list").length==0 && !$(e.target).is(".part-list")) {
              $(".part-list").slideUp(100);
            }
        });
        $(".part-list ul li a").click(function(){
            $(".textpart").html($(this).html());
            $(".part-list").slideUp(100);
        });

        $(".select-all1").click(function(){
            $(".type1 input[type='checkbox']").prop("checked", $(this).is(":checked"));
        });
        $(".select-all2").click(function(){
            $(".type2 input[type='checkbox']").prop("checked", $(this).is(":checked"));
        });
        $(".btntype1").click(function(){
            $(".type-list input[type='checkbox']").prop("checked", $(this).is(":checked"));
        });
        $(".btntype2").click(function(){
            $(".type-list").slideUp(100);
        });
	/*
	$(".showevent").click(function() {
        var num = $(".imgnews.i-note").siblings(".num");
        var formev = $(".formevent");
        var notify_count = parseInt(num.text());

		if(formev.is(":hidden"))
        {
            formev.find('#not-content').empty()
            formev.show();
            formev.find('#load').show()


            $.get('/notification/get/', function(data) {
                     formev.find('#load').hide();
                     formev.find('#not-content').append(data);
                     num.text(0);
                }, 'html'
            );
		}
		else
        {
			formev.hide();
		}
	});
    */
	$(document).on('click', ".close-event", function()
    {
		$(".formevent").hide();
	});

    $(document).on('click', "#filter-link", function()
    {
		$(".filter-form, #fade-profile").show();
	});

    $(document).on('click', ".close-event", function()
    {
		$(".filter-form, #fade-profile").hide();
	});

    $(document).on('click', ".btnprofile", function()
	{
		if($("#light-profile, #fade-profile").is(":hidden"))
        {
			$("#light-profile, #fade-profile").show();
		}
		else{
			$("#light-profile, #fade-profile").hide();
		}
	});

    $(document).on('click', ".sortActive", function() {
       var parent = $(this).parents('.note');

       parent.find('input').val($(this).data('order'));
       parent.find('.sortCurr').removeClass('sortCurr').addClass('sortActive');
       $(this).removeClass('sortActive').addClass('sortCurr');

       return false;
    });
    
	$(".cpn-current").click(function(){
        var list = $(".list-cpn");

		if(list.is(":hidden"))
        {
			list.slideDown();
		}
		else
        {
			list.slideUp();
		}
	});

	$(document).on("click", ".list-cpn li a", function(){

        var selected = $(this);

		$(".cpn-current").html( selected.html() );

		$(".list-cpn").slideUp(function() {

            var id = selected.parent().data('org');

            var newURL = updateURLParameter('current-org', id);

            location.replace(newURL);
        });
	});

});

