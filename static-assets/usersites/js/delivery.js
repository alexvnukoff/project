/**
 * Delivery
 */

$(function() {

    // Для корзины
    var DELIVERY_URL = '/b2c-products/delivery.html';
    var orderByEmailButton = $('#order_by_email'),
        paypalForm = $('#paypal_form_layer > form'),
        paypalFormButton = $(paypalForm).find('input[type="image"]:first'),
        deliveryDataForm = $('#delivery_form');
        
    if (orderByEmailButton.length > 0 && paypalForm.length > 0) {    
        $(orderByEmailButton).on('click', function(event) {
            event.preventDefault();
            var url = $(this).attr('href');
            if ($('#need_delivery').is(":checked")) {
                url += '?need_delivery=true';
            }
            window.location.href = url;
            return false;
        });
    
        // Для кнопки-рисунка отправки информации на PayPal
        if (paypalFormButton.length > 0) {
            $(paypalFormButton).on('click', function(event) {
                event.preventDefault();
                if ($('#need_delivery').is(":checked")) {
                    window.location.href = DELIVERY_URL;
                } else {
                    $(paypalForm).submit();
                }
                return false;
            });        
        }
    } else if (deliveryDataForm.length > 0 && paypalForm.length > 0) {
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
