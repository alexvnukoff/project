/**
 * Created by keren on 19/02/2017.
 */

var $sizeAffectedElements = $("div, p, a");
var $LinksElements = $("a");
var $colorAffectedElements = $("div, p, a, h1, h2, h3, h4, span, body, footer, button");
var darkon = false;
var ydarkon = false;
var lighton = false;

// Storing the original size in a data attribute so size can be reset
$sizeAffectedElements.each( function(){
  var $this = $(this);
  $this.data("orig-size", $this.css("font-size") );
});

$colorAffectedElements.each( function(){
  var $this = $(this);
  $this.data("orig-bg", $this.css("background-color") );
  $this.data("orig-color", $this.css("color") );
});

function setOrigSize(){
  $sizeAffectedElements.each( function(){
        var $this = $(this);
        $this.css( "font-size" , $this.data("orig-size") );
   });
}

function changeFontSize(direction){
    $sizeAffectedElements.each( function(){
        var $this = $(this);
        var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.css( "font-size" , newFontSize );
        $.cookie("fontSize", newFontSize, { expires: 2000, path: '/' });
    });
}

function changeLinks(){
    $LinksElements.each( function(){
        var $this = $(this);
        //var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.toggleClass('underlined-link');
        // $this.css( "text-decoration" , "underline" );
        $.cookie("links", "true", { expires: 2000, path: '/' });
    });
}

function setDarkBg(){
    //if the light bg is on, first remove it.
    if(lighton){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('lightBg');
        });
        lighton = false;
    }

    if(ydarkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('ydarkBg');
        });
        ydarkon = false;
    }

    //set the dark color.
    $colorAffectedElements.each( function(){
        var $this = $(this);
        //var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.toggleClass('darkBg');
    });

    if (darkon){
        darkon = false;
    } else {
        darkon = true;
    }
}

function setYDarkBg(){
    //if the light bg is on, first remove it.
    if(lighton){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('lightBg');
        });
        lighton = false;
    }

    if(darkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('darkBg');
        });
        darkon = false;
    }

    //set the dark color.
    $colorAffectedElements.each( function(){
        var $this = $(this);
        //var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.toggleClass('ydarkBg');
    });

    if (ydarkon){
        ydarkon = false;
    } else {
        ydarkon = true;
    }
}

function setLightBg(){
    //if the light bg is on, first remove it.
    if(darkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('darkBg');
        });
        darkon = false;
    }

    if(ydarkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('ydarkBg');
        });
        ydarkon = false;
    }

    //set the light color
    $colorAffectedElements.each( function(){
        var $this = $(this);
        //var newFontSize = parseInt($this.css("font-size"))+direction;
        $this.toggleClass('lightBg');
    });

    if (lighton){
        lighton = false;
    } else {
        lighton = true;
    }

}

function setOrigBg(){
  if(darkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('darkBg');
        });
        darkon = false;
    }

    if(lighton){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('lightBg');
        });
        lighton = false;
    }

    if(ydarkon){
        $colorAffectedElements.each( function(){
            var $this = $(this);
            //var newFontSize = parseInt($this.css("font-size"))+direction;
            $this.toggleClass('ydarkBg');
        });
        ydarkon = false;
    }
}

$( document ).ready(function() {

    var appToAccess = $('<div class="krn" id="navwrapper">\
        <nav class="navbar navbar-inverse navbar-fixed-top" id="sidebar-wrapper" role="navigation">\
        <ul class="nav sidebar-nav">\
        <li class="sidebar-brand">\
        Accessibility\
        </li>\
        <li>\
           <button class="wide-btn" id="btn-decrease" onclick="changeFontSize(-1);">A-</button>\
           <button class="wide-btn" id="btn-orig" onclick="setOrigSize();">A</button>\
           <button class="wide-btn" id="btn-increase" onclick="changeFontSize(1);">A+</button>\
        </li>\
        <li>\
           <button class="wide-btn" id="link-underline" onclick="changeLinks();">Highlight links</button>\
        </li>\
        <li>\
           <button class="wide-btn dark-bg-btn" id="dark-background" onclick="setDarkBg();"></button>\
        </li>\
        <li>\
           <button class="wide-btn ydark-bg-btn" id="ydark-background" onclick="setYDarkBg();"></button>\
        </li>\
        <li>\
           <button class="wide-btn light-bg-btn" id="light-background" onclick="setLightBg();"></button>\
        </li>\
        <li>\
           <button class="wide-btn" id="orig-background" onclick="setOrigBg();">Reset changes</button>\
        </li>\
        <li>\
           <button class="btn btn-link access-link-declare" data-toggle="modal" data-target="#accessModal">Declaration of accessibility</button>\
        </li>\
        </ul>\
        </nav>\
        \
        <div>\
        <button type="button" class="hamburger is-closed" data-toggle="offcanvas">\
        <span class="access-btn fa fa-wheelchair"></span>\
        </button>\
        </div>\
        \
        <div class="modal fade" id="accessModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel">\
          <div class="modal-dialog" role="document">\
            <div class="modal-content">\
              <div class="modal-header">\
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>\
                <h4 class="modal-title" id="myModalLabel">הצהרת נגישות</h4>\
              </div>\
              <div class="modal-body" id="accesDecaration">\
                \
              </div>\
              <div class="modal-footer">\
                <button type="button" class="btn btn-default" data-dismiss="modal">סגור</button>\
              </div>\
            </div>\
          </div>\
        </div>\
        </div>');

    var accessDeclaration = "Our objective of making our website accessible is to create a website that is available, " +
            "convenient and user friendly for people with hand or vision disabilities or other difficulties " +
            "and to enable all to surf the site easily and quickly and to benefit from the content at the site." +
            "\u003cbr\u003e" +
            "The website is supported by standard browsers. Support for Internet Explorer is from version 10 and higher." +
            "\u003cbr\u003e" +
            "The contents at the website were written in a simple and clear manner." +
            "\u003cbr\u003e" +
            "There is an accessibility menu at the top right hand side of each page with the following options:" +
            "\u003cbr\u003e" +
            "Contrast, Font Size and Links." +
            "\u003cbr\u003e" +
            "We will continue to preserve and improve the level of accessibility of the website from a perspective of equality of rights and equality of opportunity for all." +
            "\u003cbr\u003e" +
            "Should you, in any case, come across a difficulty, we will be happy to receive any response, idea and suggestion on the matter via email";

    $('#accessDialog').append(appToAccess);
    $('#accesDecaration').append(accessDeclaration);

    var trigger = $('.hamburger'),
      overlay = $('.overlay'),
     isClosed = false;

    trigger.click(function () {
      hamburger_cross();
    });

    function hamburger_cross() {

      if (isClosed == true) {
        overlay.hide();
        trigger.removeClass('is-open');
        trigger.addClass('is-closed');
        isClosed = false;
        $('#sidebar-wrapper').width("0");
      } else {
        overlay.show();
        trigger.removeClass('is-closed');
        trigger.addClass('is-open');
        isClosed = true;
        $('#sidebar-wrapper').width("220px");
      }
    }

      // $('[data-toggle="offcanvas"]').click(function () {
      //       $('#sidebar-wrapper').toggleClass('.toggled-sidbar-width');
      // });
});
