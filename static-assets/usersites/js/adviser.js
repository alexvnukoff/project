/**
 * Online adviser
 */

var START_TIMEOUT = 2000;
var ADVISER_ID = 'online_adviser';
var ADVISER_DIALOG_ID = 'online_adviser_dialog';
var ADVISER_URL = '/messages/adviser/';

function initAdviser() {
    // Слой для вызова 
    var isLoaded = false;
    var adviserMainDiv =  $('<div/>').addClass('online_adviser').attr('id', ADVISER_ID);
    $(adviserMainDiv).html('<span>Online-adviser</span>').hide();
    $('body').append(adviserMainDiv);
    
    // Слой для диалога
    var adviserMainDialogDiv = $('#' + ADVISER_DIALOG_ID); 
    if (adviserMainDialogDiv.length == 0) {
        adviserMainDialogDiv = $('<div/>').attr('id', ADVISER_DIALOG_ID);
        $(adviserMainDialogDiv).hide();
        $('body').append(adviserMainDialogDiv);
    }
    var launcherPosition = $(adviserMainDiv).position(),
        launcherWidth = $(adviserMainDiv).width();
    
    $(adviserMainDialogDiv).dialog({
        autoOpen: false,
        height: 450,
        width: launcherWidth + 250,
        minWidth: launcherWidth + 250,
        position: { my: 'center center-250', of: '#' + ADVISER_ID},
    });
    $(adviserMainDiv).click(function(event) {
        event.preventDefault();
        if (!isLoaded) {
            $.getJSON(ADVISER_URL, function(data) {
                if ('title' in data) {
                    $(adviserMainDialogDiv).dialog('option', 'title', data.title);
                }
                if ('msg' in data) {
                    $(adviserMainDialogDiv).html(data.msg);
                }
                var action = ($(adviserMainDialogDiv).dialog('isOpen')) ? 'close' : 'open';
                $(adviserMainDialogDiv).dialog(action);
                isLoaded = true;
            });
        } else {
            var action = ($(adviserMainDialogDiv).dialog('isOpen')) ? 'close' : 'open';
            $(adviserMainDialogDiv).dialog(action);
        }
        return false;                          
    });
    $(adviserMainDiv).show('slow');
}

$(function() {
    // Время запуска после загрузки страницы
    
    // Запуск
    setTimeout(initAdviser, START_TIMEOUT);

});
