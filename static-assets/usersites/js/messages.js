/**
 * Messages
 */

$(function() {

    var process_data_form_id = '#new_message_form',
        process_data_submit_id = '#save_new_message';
 
    $(document).on('click', process_data_submit_id, function(e) {
        e.preventDefault(); 
        $('.field-error').empty().addClass('error-hidden');
        $('.form-group .has-error').removeClass('has-error');
        $(process_data_form_id).ajaxSubmit({
            url: this.href,
            type: 'post',
            success: function(data) {
                if (data.code == 'error') {
                    $.each(data.errors, function(field_name, field_errors) {
                        var fieldId = '#id_' + field_name,
                            fieldErrorId = fieldId + '_errors',
                            field = $(fieldId),
                            fieldError = $(fieldErrorId),
                            fieldParentDiv = $(field).parent();
                        
                        $(fieldError).html(field_errors); 
                        $(fieldError).removeClass('error-hidden');
                        $(fieldParentDiv).addClass('has-error');
                    });
                } else if (data.code == 'success') {
                    $('#chat_tabs a[href="#chats"]').tab('show');  
                }
            }
        });
        return false;
	});
	
	// Список чатов и его обработка
	var chats = $('#chats');
	if (chats.length) {
    	var chatsUI = new ChatsUI(chats);
    	chatsUI.init();
    }
});

function _id(id_str) {
    return (typeof id_str == 'string') ? '#' + id_str : '';
}

function _cls(cls_str) {
    return (typeof cls_str == 'string') ? '.' + cls_str : '';
}

function ChatsUI(chats) {
    this.chatsListID = 'chats_list';
    this.messagesListIO = 'messages_list';
    this.itemCls = 'list-group-item';
    this.activeItemCls = 'active-item';
    this.currentItem = null;
    this.selectItemCls = 'li.' + this.itemCls;
} 

ChatsUI.prototype.init = function() {
    var self = this;    
    self.chatsList = $(_id(self.chatsListID));
    if (!self.currentItem) {
        firstItem = $(self.chatsList).find(_cls(self.itemCls) + ':first');
        if (firstItem.length > 0) {
            self.activateItem(firstItem);
            self.drawMessages(self.currentItem);
        }
    }
    $(self.selectItemCls).on('click', function(event) {
        self.onSelectItem(this);
    });
}


ChatsUI.prototype.activateItem = function(item) {
    var self = this;
    var prevItem = $(self.chatsList).find(_cls(self.activeItemCls));
    if (prevItem.length) {
        $(prevItem).removeClass(self.activeItemCls);
    }
    self.currentItem = item;
    $(self.currentItem).addClass(self.activeItemCls);
}

ChatsUI.prototype.onSelectItem = function(item) {
    var self = this;
    self.activateItem(item);
}

ChatsUI.prototype.drawMessages = function(currentItem) {
    
}

