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
            if ('msg' in data) {
                $(send_message_id).html(data.msg).dialog('open');
            }
        });
        return false;
    });                                                    

    $(document).on('click', '#send-chat-message', function(e) {
        e.preventDefault(); 
        $('#send-message-form').ajaxSubmit({
            url: this.href,
            type: 'post',
            success: function(data) {
                if (data.code == 'success') {

                } else if (data.code == 'error') {
                    $.each(data.errors, function(index, item) {
                        var p_errors = $('#' + index + '_errors');
                        if (p_errors.length) {
                            p_errors.html(item).toggle('hide-errors');
                        }
                    });
                } else {
                
                }
            }
        });
        return false;
	});

});                                                    