/**
 * Created by EC on 12/09/2016.
 */
/*
Accessiblility plu gun for n24online.com websites.

The requerments:
Text size - change the text size to a bigger or smaller one.
Contrast - Change the contrast in the document.
Links - make all links with underline.
Clear - clear all changes.


All changes will be saved on the user computer in a cookie file.
Every change will be save after confirmation.

Using the plugin:
Add in the script tag on the page where you want it:
$(function(){
    $('div.accessibility').accessMySite();
})();

Add after the body tag:
<div class="accessibility"></div>

Options in the plugin:
color - change the color of the background. (default: blue).
width - change the width. (default: 50px).
height - change the height. (default: 50px).
position - change the position. (default: right 0, top 10px).

Building a plugin:
http://brolik.com/blog/how-to-create-a-jquery-plugin/#Getting_Started

source for accessibilty code:
https://plugins.jquery.com/tag/accessibility/

 */

//init the cookies items if not done before
var initCookies = function () {
    if($.cookie("firstTime") == undefined ){
        $.cookie("firstTime", "False", { expires: 2000, path: '/' });
        $.cookie("fontSize", "", { expires: 2000, path: '/' });
        $.cookie("color", "", { expires: 2000, path: '/' });
        $.cookie("links", "false", { expires: 2000, path: '/' });
    }
};

/*
http://stackoverflow.com/questions/34656142/effective-way-of-increasing-decreasing-font-size-of-all-elements-on-page
http://richardflick.com/2013/07/28/adjusting-font-size-with-jquery/
 */

var $affectedElements = $("p"); // Can be extended, ex. $("div, p, span.someClass")
var $LinksElements = $("a");

// Storing the original size in a data attribute so size can be reset
$affectedElements.each( function(){
  var $this = $(this);
  $this.data("orig-size", $this.css("font-size") );
});

function setOrigSize(){
  $affectedElements.each( function(){
        var $this = $(this);
        $this.css( "font-size" , $this.data("orig-size") );
   });
}

function changeFontSize(direction){
    $affectedElements.each( function(){
        var $this = $(this);
        var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.css( "font-size" , newFontSize );
        $.cookie("fontSize", newFontSize, { expires: 2000, path: '/' });
    });
}

function changeBgColor(colorBg){
    $('body').css("background-color", colorBg);
    //$.cookie("color", null);
    if($.cookie("color")) {
        $.cookie("color", colorBg, {expires: 2000, path: '/'});
    }
}

function changeLinks(){
    $LinksElements.each( function(){
        var $this = $(this);
        //var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.css( "text-decoration" , "underline" );
        $.cookie("links", "true", { expires: 2000, path: '/' });
    });
}

function clearAllStyling(){
    //clearing the font size and saving the orig in the cookie
    var initFontSize = $("p").css("font-size");
    $.cookie("fontSize", initFontSize, { expires: 2000, path: '/' });
    setOrigSize();

    //clearing the color
    $.cookie("color", "none", { expires: 2000, path: '/' });
    $('body').css("background-color", "inherit");

    $.cookie("links", "false", { expires: 2000, path: '/' });
    $LinksElements.each( function(){
        var $this = $(this);
        $this.css( "text-decoration" , "none" );
    });
}

var createModelBox = function(){


    var modelCode = $('<div class="krn dialog" title="Accessibilty">\
        <p>Choose the option you want and click the confirm button.</p>\
        <h3>Change font size</h3>\
        <button id="btn-decrease" onclick="changeFontSize(-1);">A-</button>\
        <button id="btn-orig" onclick="setOrigSize();">A</button>\
        <button id="btn-increase" onclick="changeFontSize(1);">A+</button><br/><hr/>\
        <h3>Change color</h3>\
        <ul class="accessColor">\
        <li class="redBg" onclick="changeBgColor(\'red\')"></li>\
        <li class="whiteBg" onclick="changeBgColor(\'white\')"></li>\
        <li class="blackBg" onclick="changeBgColor(\'black\')"></li>\
        <li class="orangeBg" onclick="changeBgColor(\'orange\')"></li>\
        <li class="greenBg" onclick="changeBgColor(\'green\')"></li>\
        <li class="yellowBg" onclick="changeBgColor(\'yellow\')"></li>\
        <li class="purpleBg" onclick="changeBgColor(\'purple\')"></li>\
        <li class="aquaBg" onclick="changeBgColor(\'aqua\')"></li></ul><br/><br/><br/><br/><hr/>\
        <button id="link-underline" onclick="changeLinks();">Underline Links</button>\
        </div>');

     modelCode.dialog({
        resizable: false,
        height:550,
        modal: true,
        buttons: {
            "Confirm": function() {
                $( this ).dialog( "close" );
            },
            "Clear All": function() {
               clearAllStyling();
            }
        }
    });
};


//changing the color of the accessibility button
function setInitApearance(mainColor, topElem){
    $('#accessDialog').css("background-color", mainColor);
    $('#accessDialog').css("top", topElem);
}

(function ($, window, document, undefined) {
    "use strict";


        initCookies();
        //createModelBox();

})(jQuery);

(function() {
    //loading the cookies value when loading the page
    //if you have a fontsize cookie, get the font size

    if($.cookie("fontSize")) {
        var cookieFontsize = $.cookie('fontSize');

        $affectedElements.each(function () {
            var $this = $(this);
            $this.css("font-size", cookieFontsize);
        });
    }

    //if you have the color cookie, get the color
    if($.cookie("color")) {
        var cookieBgColor = $.cookie("color");
        $('body').css("background-color", cookieBgColor);
    }

    if($.cookie("links")) {
        var linksUnderline = $.cookie("links");
        changeLinks();
    }

    setInitApearance(document.getElementById("colorAccess").value,
            document.getElementById("topPosAccess").value);

})();