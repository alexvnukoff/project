/**
 * The functions for Questionnaires application
 */
 
$(function() {
    var processDataDialogDivId = 'processDataDialog',
        processDataDialogId = '#' + processDataDialogDivId,
        processDataDialog = $(processDataDialogId);

    if (processDataDialog.length == 0) {
        var processDataDialog = $('<div/>')
            .attr('height', 300)
            .attr('id', processDataDialogDivId)
            .hide();
        $('body').children(':first').prepend(processDataDialog);
    }

    var processDataDialog = $(processDataDialogId).dialog({
        autoOpen: false,
        // minHeight: 200,
        minWidth: 520, 
        modal: true,
        draggable: true,
        resizable: true,
        dialogClass: 'turnon-ui',
    });

    $(document).on('click', '.show-in-dialog', function(e) {
        e.preventDefault();
        var url = this.href,
            title = $(this).data('title');
        title = (title) ? title : 'Process data';
        $.getJSON(url, function(data) {
            if ('msg' in data) {
                $(processDataDialog).dialog('option', 'title', title);
                $(processDataDialog).html(data.msg).dialog('open');
                $(processDataDialog).dialog('widget').css('height', 'auto');
                $(processDataDialog).dialog('option', 'position', 'center')
            }
        });
        return false;
    });
});
