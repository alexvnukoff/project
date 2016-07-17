/**
 * Messages
 */

$(function() {

	// Список чатов и его обработка
	var chats = $('#chats');
	var chatsUI = null;
	if (chats.length) {
    	var chatsUI = new ChatsUI(chats);
    	chatsUI.init();
    }

    $(document).on('click', '.save-new-message', function(e) {
        e.preventDefault(); 
        var processed_form = $(this).parents('form:first');
        $(processed_form).find('.field-error').empty().addClass('error-hidden');
        $(processed_form).find('.form-group .has-error').removeClass('has-error');
        $(processed_form).ajaxSubmit({
            url: this.href,
            type: 'post',
            success: function(data) {
                $(this).prop('disabled', true);
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
                    $(processed_form).clearForm();
                    if (chatsUI) {
                        chatsUI.drawChats();
                    }
                    $('#chat_tabs a[href="#chats_list_tab"]').tab('show');  
                }
                $(this).prop('disabled', false);
            }
        });
        return false;
	});
	
});

function _id(id_str) {
    return (typeof id_str == 'string') ? '#' + id_str : '';
}

function _cls(cls_str) {
    return (typeof cls_str == 'string') ? '.' + cls_str : '';
}

function ChatsUI(chats) {
    this.chatsListID = 'chats_list';
    this.chatMessagesID = 'chat_messages';
    this.messagesListID = 'messages_list';
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
    self.drawMessages(self.currentItem);
}

ChatsUI.prototype.drawChats = function() {
    var self = this;    
    self.chatsList = $(_id(self.chatsListID));
    var url = '/messages/chats/refresh/';
    $.get(url, function(data) {
        $(self.chatsList).html(data);
        self.currentItem = null;
        self.init();
    });
}

ChatsUI.prototype.drawMessages = function(currentItem) {
    var self = this;
    var messagesList = $(_id(self.messagesListID));
    if (messagesList.length > 0){
        var item_a = $(currentItem).children('a:first'),
            chat_id = item_a.data('chat-id'),
            url = item_a.data('url');

        if (chat_id && url) {
            $('#new_message_chat_id').val(chat_id);
            $.get(url, function(data) {
                $(messagesList).html(data);
                messagesList.scrollTop(messagesList[0].scrollHeight);
            });
        }
    }    
}

