
$(document).ready(function() {


        $(document).on("click", ".add-advandce", function() {
            var formin = $('.append-formin');
            var num =  parseInt(formin.find("#count").val()) ;
            var dataPost = {"NUMBER": num};
            if (num >= 5)
                return false

              $.get('/addPage/get/',dataPost, function(data) {
                     $(".append-formin").append(data);
                     formin.find("#count").val(num + 1);

                }, 'html');


            return false
        });


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
	
	$("#showevent").click(function() {
        var num = $(".imgnews.i-note").siblings(".num").text()
        var formev = $(".formevent")

		if(formev.is(":hidden") && parseInt(num)>0)
        {

            formev.find('#not-content').empty()
            formev.show();
            formev.find('#load').show()


            $.get('/notification/get/', function(data) {
                     formev.find('#load').hide()
                     formev.find('#not-content').append(data)
                }, 'html'
            );
		}
		else
        {
			formev.hide();
		}
	});

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
});

function UpdateQueryString(key, value, url) {
    if (!url) url = window.location.href;
    var re = new RegExp("([?&])" + key + "=.*?(&|#|$)(.*)", "gi");

    if (re.test(url)) {
        if (typeof value !== 'undefined' && value !== null)
            return url.replace(re, '$1' + key + "=" + value + '$2$3');
        else {
            var hash = url.split('#');
            url = hash[0].replace(re, '$1$3').replace(/(&|\?)$/, '');
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
    }
    else {
        if (typeof value !== 'undefined' && value !== null) {
            var separator = url.indexOf('?') !== -1 ? '&' : '?',
                hash = url.split('#');
            url = hash[0] + separator + key + '=' + value;
            if (typeof hash[1] !== 'undefined' && hash[1] !== null)
                url += '#' + hash[1];
            return url;
        }
        else
            return url;
    }
}