/**
 * Delivery
 */

$(function() {
    var deliveryDataForm = $('#delivery_form'), 
        paypalForm = $('#paypal_form_layer > form'),
        paypalFormButton = $(paypalForm).find('input[type="image"]:first');
    if (paypalFormButton.length > 0) {
        $(paypalFormButton).on('click', function(event) {
            event.preventDefault();
            $('.form_field_error').each(function() {
                $(this).hide('hide_layer');
            });
            $(deliveryDataForm).ajaxSubmit({
                url: this.href,
                type: 'post',
                success: function(data) {
                    if (data.code == 'success') {
                        $(paypalForm).submit();
                    } else if (data.code == 'error') {
                        $.each(data.errors, function(index, item) {
                            var p_errors = $('#' + index + '_errors');
                            if (p_errors.length) {
                                p_errors.html(item).toggle('hide-errors');
                            }
                        });
                    }
                }
            });
            return false;
        });        
    }
});
