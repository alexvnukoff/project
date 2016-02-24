/*
 * UI for messages and chats
 */

function addOneMoreInput(input_name, cls_selector) {
    $('.' + cls_selector).last().change(function() {
        $(this).after('<input name="' + input_name +'" class="' + cls_selector + '" type="file" />');
        $(this).off('change');
        addOneMoreInput(input_name, cls_selector);
    });
}

 
$(function() {

    var send_message_id = '#send-message-dialog';
    
    $(send_message_id).dialog({
        autoOpen: false,
        minHeight: 600,
        minWidth: 520, 
        modal: true,
        draggable: true,
        resizable: true,
        title: 'Send message',
        dialogClass: 'turnon-ui',
    });

    $('.contact-us').click(function(event) {
        event.preventDefault();
        $.getJSON(this.href, function(data) {
            if ('html' in data) {
                if (data.code == 'success') {
                    $(send_message_id).html(data.html).dialog('open');
                } else if (data.code == 'error') {
                    var error_msg = '<p class="errors">' + data.html + '</p>';
                    $(send_message_id).html(error_msg).dialog('open');
                }
            }
        });
        return false;
    });                                                    
});                                                    