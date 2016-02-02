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
    });
