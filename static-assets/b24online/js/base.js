var statciPath = '/static/b24online/';
var LANG = {};
$(document).ready(function() {
  $(".fancybox").fancybox({
    openEffect	: 'none',
    closeEffect	: 'none'
  });
});

$(document).ready(function(e) {
  $('#thumbs').delegate('img','click', function(){
    $('#largeImage').attr('src',$(this).attr('src').replace('thumb','large'));
  });
});

$(document).ready(function() {
  ui.init();
  uiDetail.init();
  uiEvents.init();
});

$(function() {
  var cname = 'tab';
  var ca = document.cookie.split(';');
  var name = cname + "=";
  var tab = 0;

  for(var i=0; i < ca.length; i++) {
     var c = ca[i].trim();

     if (c.indexOf(name)==0) {
        tab = c.substring(name.length, c.length);
        break;
     }
   }

  $( "#tabs" ).tabs({
    active: tab,
    activate: function(event, ui) {
      var i = ui.newTab.index();

      document.cookie = cname + "=" + i + "; path=/";
    }
  });
  $( ".tabfilter" ).tabs();
});

LANG['structure'] = {
    'confirm': 'Do you want to delete this record?',
    'popup_ok': 'OK',
    'popup_cancel': 'Cancel',
    'popup_dep': 'Department name',
    'popup_vac': 'Vacancy title',
    'popup_vac_title': 'Add the vacancy',
    'popup_loading': 'Loading...',
};

LANG['staff'] = {
    'confirm': 'Do you want to delete this record?',
    'popup_add': 'OK',
    'popup_cancel': 'Cancel',
    'popup_dep': 'Department name',
    'popup_vac': 'Vacancy title',
    'popup_administrator': 'Administrator',
    'popup_title': 'Add staff',
    'popup_user_title': 'Add user email',
    'popup_title_edit': 'Edit staff',
    'popup_loading': 'Loading...',
    'select_department': 'Select department',
    'select_vacancy': 'Select vacancy',
    'popup_hidden_user': 'Do not show user',
    'extra_permissions_title': 'Select additional permissions',
    'popup_staffgroup': 'Related to staff group',
    'popup_for_children': 'Use permissions for child companies',
};

var STAFFGROUPS = [

      {"value": 1, "name": "Admins"},

      {"value": 2, "name": "Editors"},

      {"value": 3, "name": "Financiers"},

      {"value": 4, "name": "Staff"},

      {"value": 5, "name": "Writers"},

];
var EXTRAGROUPS = [

      {"value": 7, "name": "Banners"},

      {"value": 5, "name": "Business Proposals"},

      {"value": 10, "name": "Deals"},

      {"value": 6, "name": "Exhibitions"},

      {"value": 4, "name": "Innovation Projects"},

      {"value": 1, "name": "News"},

      {"value": 3, "name": "Organizations"},

      {"value": 2, "name": "Products"},

      {"value": 8, "name": "Site"},

      {"value": 9, "name": "Vacancies"},

];
