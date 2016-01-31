/**
 * Js for stats
 */
$(function() {
    $( ".date" ).datepicker({
        changeMonth: true,
        changeYear: true,
        yearRange: "1900:",
        dateFormat: "dd/mm/yy"
      });
});

$(document).ready(function () {
    // Stats data table rows toggling
    $('.toggle-next').not('.force-open').each(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
      	$(this).nextAll(child_class).hide();		    
    });
    $('.toggle-next.force-open').addClass('toggled');
  	$('.toggle-next').click(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
        $(this).toggleClass('toggled').nextAll(child_class).toggle();	
    });

    // Modal dialogues for charts
    $('#bardialog').dialog({
        autoOpen: false,
        minWidth: 800,
        minHeight: 400,
        modal: true,
    });
    $(".stats_detail").on("click", function(e) {
        e.preventDefault();
        $("#bardialog").html("");
        $("#bardialog").dialog("open");
        $("#bardialog").load(this.href);
        return false;
    });
    
    $('#diagdialog').dialog({
        autoOpen: false,
        minWidth: 500,
        minHeight: 500,
        modal: true,
    });
    $(".stats_diag").on("click", function(e) {
        e.preventDefault();
        $("#diagdialog").html("");
        $("#diagdialog").dialog("open");
        $("#diagdialog").load(this.href);
        return false;
    });
});
