$(document).ready(function() {
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

	$(".close-event").click(function()
    {
		$(".formevent").hide();
	});

	$("#filter-link").click(function()
    {
		$(".filter-form, #fade-profile").show();
	});

	$(".close-event").click(function()
    {
		$(".filter-form, #fade-profile").hide();
	});

	$(".btnprofile").click(function(){
		if($("#light-profile, #fade-profile").is(":hidden"))
        {
			$("#light-profile, #fade-profile").show();
		}
		else{
			$("#light-profile, #fade-profile").hide();
		}
	});
});