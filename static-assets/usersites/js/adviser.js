/**
 * Online adviser
 */

var START_TIMEOUT = 2000,
    ADVISER_ID = 'online_adviser',
    ADVISER_PANEL_ID = 'online_adviser_panel',
    ADVISER_URL = '/messages/adviser/';

function formatState(opt) {
    /**
     * Format the select2 option text (name + avatar)
     */
    var optimage = $(opt.element).data('image'); 
    if (!optimage) {
        return opt.text;
    } else {                    
        var $opt = $('<span><img src="' + optimage + '" width="23px" /> ' + opt.text + '</span>');
        return $opt;
    }
};


function initAdviser() {
    /**
     * Initialize the online adviser
     */
    var isLoaded = false;

    // Add the neccessary layers
    var adviserPanel = $('<div/>')
        .addClass('panel').
        .addClass('panel_default')
        .attr('id', ADVISER_PANEL_ID).hide();
    $('body').append(adviserPanel);

    var adviserMainDiv = $('<div/>')
        .addClass('online_adviser')
        .attr('id', ADVISER_ID);
    $(adviserMainDiv).html('<span>Online-adviser</span>').hide();
    $('body').append(adviserMainDiv);
    
    $(adviserMainDiv).click(function(event) {
        event.preventDefault();
        var self = this;
        if (!isLoaded) {
            $.get(ADVISER_URL, function(data) {
                if (data) {
                    $(self).hide();
                    $(adviserPanel).html(data).show('slow');
                    isLoaded = true;
                }
            });
        }
        return false;                          
    });
    $(adviserMainDiv).show('slow');
}

$(function() {
    // Call the Adviser initializer
    setTimeout(initAdviser, START_TIMEOUT);
});
