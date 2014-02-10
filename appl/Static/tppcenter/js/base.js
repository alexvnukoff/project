$(document).ready(function() {
    $("#country").click(function(){
		if($(".country-list").is(":hidden")){
			$(".country-list").show();
		}
		else{
			$(".country-list").hide();
		}
	});
	$(document).mouseup(function(e) {
		if($(e.target).parents(".country-list").length==0 && !$(e.target).is(".country-list")) {
		  $(".country-list").hide();
		}
	});
	$(".country-list ul li a").click(function(){
		$(".textfilter").html($(this).html());
		$(".country-list").hide();
	});
	//Type droplist
	$("#type").click(function(){
		if($(".type-list").is(":hidden")){
			$(".type-list").show();
		}
		else{
			$(".type-list").hide();
		}
	});
	$(document).mouseup(function(e) {
		if($(e.target).parents(".type-list").length==0 && !$(e.target).is(".type-list")) {
		  $(".type-list").hide();
		}
	});
	$("i.i-close").click(function(){
		$(this).parent().parent().hide();
	});
});