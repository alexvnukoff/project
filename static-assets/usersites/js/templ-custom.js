
// dotdotdot fot template_name
$(document).ready(function() {
	$(".teplate_list__name--dotdotdot").dotdotdot();
});
// dotdotdot fot template_name


$(".fancybox-effects-a").fancybox({
    helpers: {
        title : {
            type : 'outside'
        },
        overlay : {
            speedOut : 0
        }
    }
});



/**
 * Created by taksenov@gmail.com on 10.01.2016.
 */

(function() {

    var app = {

        // -- init js
        initialize : function () {
            var _this = this;

            _this.setUpListeners();

        },
         // -- init js

        // -- setup listeners
        setUpListeners: function () {

            // -- chooseTheTemplate
            $('.template_list__btn_pick').on('click', app.chooseTheTemplate);

        },
        // -- setup listeners

        // -- func loaded from setUpListeners ===============

		// chooseTheTemplate
        chooseTheTemplate: function () {

            var _this = $(this),
                templateId = $(this).data('template-id'),
                divDeleteCheck = $('.template_list__block--empty'),
                imgDeleteOpacity = $('.template_list__img--empty')
                ;

            divDeleteCheck.removeClass('template_list__block--active');
            imgDeleteOpacity.removeClass('template_list__img--active');

            var divAddCheck = $(this).parentsUntil('.template_list__block').prev('.template_list__block--empty');
            var imgAddOpacity = $(this).parentsUntil('.template_list__block').children('.template_list__img').find('.template_list__img--empty');

            divAddCheck.addClass('template_list__block--active');
            imgAddOpacity.addClass('template_list__img--active');
            $('#input_user_template').val(templateId);
        },
		// chooseTheTemplate

        // -- empty func
        someEmptyFunctuion: function () {}
        // -- empty func

        // -- func loaded from setUpListeners ===============

    }

    app.initialize();

}());











