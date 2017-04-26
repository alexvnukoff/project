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
        נגישות\
        </li>\
        <li>\
           <button class="wide-btn" id="btn-decrease" onclick="changeFontSize(-1);">א-</button>\
           <button class="wide-btn" id="btn-orig" onclick="setOrigSize();">א</button>\
           <button class="wide-btn" id="btn-increase" onclick="changeFontSize(1);">א+</button>\
        </li>\
        <li>\
           <button class="wide-btn" id="link-underline" onclick="changeLinks();">הדגש קישורים</button>\
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
           <button class="wide-btn" id="orig-background" onclick="setOrigBg();">איפוס שינויים</button>\
        </li>\
        <li>\
           <button class="btn btn-link access-link-declare" data-toggle="modal" data-target="#accessModal">הצהרת נגישות</button>\
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

    var accessDeclaration = "אינטרנט מהווה כיום את המאגר הגדול ביותר לחופש המידע עבור כלל המשתמשים, ומשתמשים בעלי מוגבלויות בפרט. " +
            "ככזה, אנו שמים חשיבות רבה במתן אפשרות שווה לאנשים עם מוגבלות לשימוש במידע המוצג באתר, ולאפשר חווית גלישה טובה יותר." +
            "\u003cbr\u003e" +
            "אנו שואפים להבטיח כי השירותים הדיגיטליים יהיו נגישים לאנשים עם מוגבלויות, ועל כן הושקעו משאבים רבים להקל את השימוש באתר עבור אנשים עם מוגבלויות, ככל האפשר, מתוך אמונה כי לכל אדם מגיעה הזכות לחיות בשוויון, כבוד, נוחות ועצמאות." +
            "\u003cbr\u003e" +
            "באתר מוצב תפריט הנגשה. לחיצה על התפריט מאפשרת פתיחת כפתורי ההנגשה." +
            "\u003cbr\u003e" +
            "חרף מאמצנו לאפשר גלישה באתר נגיש עבור כל דפי האתר, יתכן ויתגלו דפים באתר שטרם הונגשו, או שטרם נמצא הפתרון הטכנולוגי המתאים." +
            "אנו ממשיכים במאמצים לשפר את נגישות האתר, ככל האפשר, וזאת מתוך אמונה ומחויבות מוסרית לאפשר שימוש באתר לכלל האוכלוסייה, לרבות אנשים עם מוגבלויות." +
            "\u003cbr\u003e" +
            "על נגישות המקום תוכלו לקרוא בעמוד הנגישות באתר." +
            "\u003cbr\u003e" +
            "להערות, שאלות והצעות ניתן לפנות אלינו דרך דף צור קשר שבאתר.";

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






