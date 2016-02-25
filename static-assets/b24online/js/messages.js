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
    var send_message_diag = $(send_message_id).dialog({
        autoOpen: false,
        minHeight: 600,
        minWidth: 520, 
        modal: true,
        draggable: true,
        resizable: true,
        dialogClass: 'turnon-ui',
    });

    $(document).on('click', '.contact-us', function(e) {
        e.preventDefault();
        if ('href' in this) {
            var url = this.href;
        } else {
            var organization_id = $(this).data('organization-id'),
                recipient_id = $(this).data('recipient-id');
            var url = '/messages/send/user/' + recipient_id + '/';
        }
        $.getJSON(url, function(data) {
            if ('msg' in data) {
                $(send_message_diag).dialog('option', 'title', 'Send message');
                $(send_message_diag).html(data.msg).dialog('open');
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
                    if ('redirect_to_chat' in data) {
                        window.location.href = data.redirect_to_chat;
                    } 
                    if ($(send_message_diag).dialog('isOpen')) {
                        $(send_message_diag).dialog('close');
                    }
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

    $(document).on('click', '#add_participant', function(e) {
        e.preventDefault();
        var url = this.href;
        $.getJSON(url, function(data) {
            if ('msg' in data) {
                $(send_message_diag).dialog('option', 'title', 'Add new chat participant');
                $(send_message_diag).dialog('option', 'minHeight', 200);
                $(send_message_diag).html(data.msg).dialog('open');
                $(send_message_diag).dialog("widget").css('height', 'auto');
            }
        });
        return false;
    });


});                                                    