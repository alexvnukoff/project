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

    var process_data_dialog_id = '#process-data-dialog',
        process_data_form_id = '#process-data-form',
        process_data_submit_id = '#process-data-submit',
        process_data_cancel_id = '#process-data-cancel';
    
    var process_data_dialog = $(process_data_dialog_id).dialog({
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
                $(process_data_dialog).dialog('option', 'title', 'Send message');
                $(process_data_dialog).dialog('option', 'minHeight', 600);
                $(process_data_dialog).html(data.msg).dialog('open');
                $(process_data_dialog).dialog("widget").css('height', 'auto');
            }
        });
        return false;
    });

    $(document).on('click', '.call-process-form', function(e) {
        e.preventDefault();
        var url = this.href,
            title = $(this).data('title'),
            height = $(this).data('height');
        alert('OKOK: ', url);
        height = (height) ? height : 300;
        title = (title) ? title : 'Process data';
        $.getJSON(url, function(data) {
            if ('msg' in data) {
                $(process_data_dialog).dialog('option', 'title', title);
                $(process_data_dialog).dialog('option', 'minHeight', height);
                $(process_data_dialog).html(data.msg).dialog('open');
                $(process_data_dialog).dialog("widget").css('height', 'auto');
            }
        });
        return false;
    });

    $(document).on('click', process_data_submit_id, function(e) {
        e.preventDefault(); 
        $(process_data_form_id).ajaxSubmit({
            url: this.href,
            type: 'post',
            success: function(data) {
                if (data.code == 'success') {
                    if ('redirect_to_chat' in data) {
                        window.location.href = data.redirect_to_chat;
                    } 
                    if ($(process_data_dialog).dialog('isOpen')) {
                        $(process_data_dialog).dialog('close');
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

    $(document).on('click', process_data_cancel_id, function(e) {
        e.preventDefault(); 
        if ($(process_data_dialog).dialog('isOpen')) {
            $(process_data_dialog).dialog('close');
        }
        return false;
	});

    $(document).on('click', '.confirm-process', function(e) {
        return confirm('Are You sure?');
	});

});                                                    