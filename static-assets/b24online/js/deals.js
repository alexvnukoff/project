/**
 * Js for deals
 */

$(document).ready(
    function () {
	$('.toggle-next').not('.force-open').each(
	    function () {
		$(this).next().hide();		    
	    });
	$('.toggle-next.force-open').addClass('toggled');
	$('.toggle-next').click(
	    function () {
    		$(this).toggleClass('toggled').next().toggle();	
	});

    $('.toggle-child').not('.force-open').each(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
      	$(this).nextAll(child_class).hide();		    
    });
    $('.toggle-child.force-open').addClass('toggled');
  	$('.toggle-child').click(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
        $(this).toggleClass('toggled').nextAll(child_class).toggle();	
    });

	$( ".date" ).datepicker({  
        changeMonth: true,   
        changeYear: true,  
        yearRange: "2010:",   
        dateFormat: "dd/mm/yy"
    });
});
