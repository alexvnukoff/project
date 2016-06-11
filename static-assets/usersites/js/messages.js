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
                        /**
                         * Обработка ошибок формы
                         * index - имя поля, item - сообщение,
                         * необходимо:
                         *  - изменить тип поля, и приглашения;
                         *  - заполнить блок текстом сообщения;
                         *  - сделать блок видимым. 
                         */
                    
                        var fieldId = '#id_' + field_name, // ИД поля
                            fieldErrorId = fieldId + '_errors', // ИД блока для ошибки
                            field = $(fieldId), // Поле
                            fieldError = $(fieldErrorId), // Блок для ошибки
                            fieldParentDiv = $(field).parent(); // Родительский блок для поля
                        
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
});

 