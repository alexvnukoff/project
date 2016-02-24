/*
 * UI for messages and chats
 */
 
$(function() {

    var send_message_id = '#send-message-dialog';
    
    $(send_message_id).dialog({
        autoOpen: false,
        minHeight: 600,
        minWidth: 500, 
        modal: true,
        draggable: true,
        resizable: true,
        dialogClass: 'turnon-ui',
    });

    $('.contact-us').click(function(event) {
        event.preventDefault();
        $.getJSON(this.href, function(data) {
            if ('html' in data) {
                $(send_message_id).html(data.html).dialog('open');
            }
        });
        return false;
    });                                                    
});
                                                    
                                                    