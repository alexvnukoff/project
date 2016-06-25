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

    // Stats data table rows toggling
    $('.toggle-child').not('.force-open').each(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
      	$(this).nextAll(child_class).hide();
    });
    $('.toggle-child.force-open').addClass('toggled');
  	$('.toggle-child').click(function () {
        var child_class = '.' + $(this).attr('id') + '-child';
        $(this).toggleClass('toggled').nextAll(child_class).toggle();
    });

    // Modal dialogues for charts
    $('#bardialog').dialog({
        autoOpen: false,
        minWidth: 800,
        minHeight: 400,
        modal: true,
        dialogClass: 'turnon-ui',
        title: 'The Events statistics'
    });
    $(".stats_detail").on("click", function(e) {
        e.preventDefault();
        $("#bardialog").html('').dialog("open").load(this.href);
    });

    $('#diagdialog').dialog({
        autoOpen: false,
        minWidth: 500,
        minHeight: 500,
        modal: true,
        dialogClass: 'turnon-ui',
        title: 'Distributoin by countries',
    });
    $(".stats_diag").on("click", function(e) {
        e.preventDefault();
        $("#diagdialog").html('').dialog("open").load(this.href);
    });
});
