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

$(document).ready(function()
{
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

        $("#country").click(function(){
            if($(".country-list").is(":hidden")){
                $(".country-list").slideDown(100);
            }
            else{
                $(".country-list").slideUp(100);
            }
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
         $(".reg_to_exhebition").click(function(){
         var form =   $("#registration_to_ex").serializeArray();
         var o = {};

         $.each(form, function() {
             if (o[this.name] !== undefined) {
                if (!o[this.name].push) {
                    o[this.name] = [o[this.name]];
                }
                o[this.name].push(this.value || '');
            } else {
                o[this.name] = this.value || '';
            }
              });
        form = o;
        var email;
        email = /^([a-zA-Z0-9_.+-])+\@(([a-zA-Z0-9-])+\.)+([a-zA-Z0-9]{2,4})+$/;
        if (!form.name_register.trim() || !form.email_register.trim() || !email.test(form.email_register))
        {
            $("#registration_error_ex").show();
            $("#registration_succsefuly_ex").hide();

        }
        else
        {
             $("#registration_error_ex").hide();
             $("#registration_succsefuly_ex").show();
             var dataPost = {'NAME':form.name_register , 'EMAIL':form.email_register,
                             'TELEPHONE': form.telephone_register, 'COMPANY': form.company_register,
                             'POSITION': form.position_register, 'SEND_EMAIL': form.email_company_register,
                             'EXEBITION': form.ex_name_register};

             $.post('/register/exhibition/', dataPost );

        }

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

    $(document).on('click', ".contact-us", function()
    {
        $('#send_succsefuly').hide()
	    document.getElementById('light-contact').style.display='block';
        document.getElementById('fade-contact').style.display='block';

        var company_id = $(this).data('id');
        var company_name = $(this).data('name');
        $("#toCompany").val(company_id);
        $('#send_to').text(company_name);

        var user_id = $(this).data('userId');
        var user_name = $(this).data('userName');
        $("#toUser").val(user_id);
        if (typeof user_id !== "undefined") {
            $('#user-reciever-info').show();
            $('#send_to_user').text(user_name);
        }
	});
     $(document).on('click', "#cancel", function()
     {
          document.getElementById('light-contact').style.display='none';
          document.getElementById('fade-contact').style.display='none';
     });

    $(document).on('click', "#send-message", function()
    {
        $('#send_succsefuly').text("Please wait to response.....").show();
        $("#messageToCompany").ajaxSubmit({
            url: '/companies/send/',
            type: 'post',
            success:function(data) {
                    $('#send_succsefuly').text(data).show()
            }
        });
        $("#messageToCompany")[0].reset();
	});

    $(document).on('click', "#send-resume", function()
    {
        $('#send_succsefuly').hide()
	    document.getElementById('light-vacancy').style.display='block';
        document.getElementById('fade-vacancy').style.display='block';


	});

    $(document).on('click', "#cancel-vacancy", function()
    {
        document.getElementById('light-vacancy').style.display='none';
        document.getElementById('fade-vacancy').style.display='none';
    });

    $(document).on('click', "#send-vacancy", function()
    {
        $('#send_resume_succsefuly').text("Please wait to response.....").show();
        var dataPost  = {'VACANCY': $('#vacancy-id').val(),
                        'RESUME':  $('#resume-id').val()
                    };
        $.ajax({
            url: '/vacancy/send/',
            type: 'post',
            data : dataPost ,
            success:function(data) {
                    $('#send_resume_succsefuly').text(data).show()
            }
        });
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

		$(".cpn-current").html( $(this).html() );

		$(".list-cpn").slideUp();
	});

});

<!-- Share for social networks -->
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
<!-- /Share for social networks -->
