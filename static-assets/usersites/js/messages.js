/**
 * Messages
 */

$(function() {

    var process_data_form_id = '#new_message_form',
        process_data_submit_id = '#save_new_message';
 
    $(document).on('click', process_data_submit_id, function(e) {
        e.preventDefault(); 
        $(process_data_form_id).ajaxSubmit({
            url: this.href,
            type: 'post',
            success: function(data) {
                if (data.code == 'error') {
                    $.each(data.errors, function(index, item) {
                        console.log(index);
                        console.log(item);                                
                    });
                }
            }
        });
        return false;
	});
});

 