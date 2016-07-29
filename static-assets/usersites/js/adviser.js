/**
 * Online adviser
 */

var START_TIMEOUT = 2000;
var ADVISER_ID = 'online_adviser';
var ADVISER_DIALOG_ID = 'online_adviser_dialog';


function initAdviser() {
    // Слой для вызова 
    var adviserMainDiv =  $('<div/>').addClass('online_adviser').attr('id', ADVISER_ID);
    $(adviserMainDiv).html('<span>Онлайн-конультант</span>').hide();
    $('body').append(adviserMainDiv);
    
    // Слой для диалога
    var adviserMainDialogDiv = $('#' + ADVISER_DIALOG_ID); 
    if (adviserMainDialogDiv.length == 0) {
        adviserMainDialogDiv = $('<div/>').attr('id', ADVISER_DIALOG_ID);
        $(adviserMainDialogDiv).hide();
        $('body').append(adviserMainDialogDiv);
    }
    $(adviserMainDialogDiv).dialog({
        autoOpen: false
    });
    $(adviserMainDiv).click(function(event) {
        event.preventDefault();
        var launcherPosition = $(adviserMainDiv).position(),
            launcherWidth = $(adviserMainDiv).width();
        $(adviserMainDialogDiv).dialog('open');
        $(adviserMainDialogDiv).dialog('widget').css('height', '280px');
        //$(adviserMainDialogDiv).dialog('widget').css('width', launcherWidth);
        //$(adviserMainDialogDiv).dialog('widget').css('minWidth', launcherWidth);
        $(adviserMainDialogDiv).dialog('option', 'position', 'center');
        return false;                          
    });
    $(adviserMainDiv).show('slow');
}

$(function() {
    // Время запуска после загрузки страницы
    
    // Запуск
    setTimeout(initAdviser, START_TIMEOUT);

});
