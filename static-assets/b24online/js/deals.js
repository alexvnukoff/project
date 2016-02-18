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
	$( ".date" ).datepicker({  
        changeMonth: true,   
        changeYear: true,  
        yearRange: "2010:",   
        dateFormat: "dd/mm/yy"
    });
});
