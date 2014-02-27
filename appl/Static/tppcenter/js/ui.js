/**
 * Created by user on 19.02.14.
 */

$(document).ready(function() {
       function getCookie(name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;

                    }
                }
            }
            return cookieValue;
        }

        function csrfSafeMethod(method) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }

        function sameOrigin(url) {
            // test that a given url is a same-origin URL
            // url could be relative or scheme relative or absolute
            var host = document.location.host; // host + port
            var protocol = document.location.protocol;
            var sr_origin = '//' + host;
            var origin = protocol + sr_origin;
            // Allow absolute or scheme relative URLs to same origin
            return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
                (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
                // or any other URL that isn't scheme relative or absolute i.e relative.
                !(/^(\/\/|http:|https:).*/.test(url));
        }

        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
                     var csrftoken = getCookie('csrftoken');
                    // Send the token to same-origin, relative URLs only.
                    // Send the token only if the method warrants CSRF protection
                    // Using the CSRFToken value acquired earlier
                    xhr.setRequestHeader("X-CSRFToken", csrftoken);
                }
            }
        });


});


       var ui = {

            loading: null,
            loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',
            container: ".news-center .container",
            keywords: null,
            filter_form: null,
            search_form: null,
            curPage: null,
            scripts: [],
            styles: [],

           filters: {

               country: {
                   selector: '#filter-country',
                   name: 'filter[country]' //hidden input name
               },

               tpp: {
                   selector: '#filter-tpp',
                   name: 'filter[tpp]' //hidden input name
               },

               branch: {
                   selector: '#filter-branch',
                   name: 'filter[branch]' //hidden input name
               }
           },


            signals: {
                start_load: 'startPageLoad',
                end_load: 'pageLoaded',
                link_click: 'linkClicked',
                scripts_loaded: 'scriptsLoaded',
                filter_removed: 'filterRemoved'
            },

            init: function() {

                ui.curPage = $('.cur-page');
                ui.keywords = $('.keyword .list-key');
                ui.filter_form = $('form[name="filter-form"]');
                ui.search_form = $('form[name="search"]');

                if (ui.filter_form.length == 0)
                    return false;

                ui.initFilters();

                $(document).bind(ui.signals['end_load'], ui.loadScripts);
                $(document).bind(ui.signals['scripts_loaded'], ui.setPage);
                $(document).bind(ui.signals['filter_removed'], ui.filterPageLoad);

                $(document).on('click', '.single-page', ui.onClick);
                $(document).on('click', '.filter-remove', ui.onRemove);
                $(document).on('click', '#save-filter', ui.saveFilter);
                $(document).on('click', ui.container + ' .panging a', ui.pageNav);
                $(document).on('submit', 'form[name="search"]', ui.search);
            },

            search: function() {
                var val = $(this).find('input[name="q"]').val();

                if (val.length > 0 && val.length < 3)
                    return false;

                url = UpdateQueryString("q", val);
                params = url.replace(window.location.origin + window.location.pathname, '');
                ui.requester(window.location.pathname, params.substr(1));

                return false;
            },

            pageNav: function() {

                url = $(this).attr('href');

                ui.requester(url, '', true);

                return false;
            },

            saveFilter: function() {

                var filters = {};

                for (filter in ui.filters)
                {
                    field = $(ui.filters[filter].selector);

                    if (field.length == 0)
                        continue;

                    var values = field.select2('data');

                    if (values && values.length > 0)
                    {
                        filters[filter] = values;
                    }
                }

                ui.setFilters(filters, true);
                $(".filter-form, #fade-profile").hide();
                ui.filterPageLoad();

            },

            filterPageLoad: function() {
                var params = ui.filter_form.serialize();
                var search = ui.search_form.serialize();

                if (params != '')
                    params += '&' + search;
                else
                    params = search;

                ui.requester(window.location.pathname, params)

            },

            onRemove: function() { //Filter key removed

                link = $(this).parent();
                id = link.data('id');
                ui.filter_form.find('input[value="' + id + '"].filter-item').remove();
                link.parent().remove();

                //ui.initFilters();
                $(document).trigger(ui.signals.filter_removed);

            },

            initFilters: function() {//initial values for filter popup
                var filter_keys = [];

                for (filter in ui.filters)
                {
                    if (!options.hasOwnProperty(filter))
                        continue;


                    field = $(ui.filters[filter].selector);

                    if (field.length == 0)
                        continue;

                    field.data('name', filter).select2(options[filter]);

                    var data = []

                    $('input[name="filter[' + filter + '][]"].filter-item').each(function() {
                            data.push({id: $(this).val(), title: $(this).data('text')});
                            filter_keys.push(data[data.length - 1]);
                    });

                    if (data.length > 0)
                            field.select2('data', data);
                    else //clear filter
                        $(ui.filters[filter].selector).select2('val', '');
                }

                ui.setKeyFilters(filter_keys);
            },

            setKeyFilters: function(data) { //Removable filters
                keys = ''

                if (data.length > 0)
                {

                    for(i=0, len = data.length - 1; i < 5; i++)
                    {
                        keys += '<li>' + data[i].title + '<a href="#" data-id="' + data[i].id + '">' +
                            '<i class="i-close filter-remove imgnews"></i></a></li>';

                        if (len == i)
                            break
                    }

                }

                ui.keywords.html(keys);
            },

            onClick: function() { //On menu click
                $(document).trigger(ui.signals.link_click, $(this));
                ui.search_form.find('input[name="q"]').val('');

                url = $(this).attr('href');
                text = $(this).text();
                ui.curPage.text(text);

                ui.loading = ui.requester(url);

                return false;
            },

            loadScripts: function(event, url, data) { //load addition scripts
                var head = $('head');

                styles = data['styles'];
                scripts = data['scripts'];

                for (i in styles)
                {
                    $('<link>').attr({
                      rel:  "stylesheet",
                      type: "text/css",
                      href: styles[i]
                    }).appendTo(head);
                }

                if (scripts.length > 0)
                    $.getScript(scripts);

                setTimeout(function() {
                    $(document).trigger(ui.signals['scripts_loaded'], [data])
                }, 500);
            },

            setPage: function(event, data){
                ui.setFilters(data.filters);

                $(ui.container).replaceWith( data.content );
                ui.filter_form = $('form[name="filter-form"]');
                ui.initFilters();
            },

            clearer: function() { //clear all filters
                ui.filter_form.find('input[name].filter-item').remove();
            },

           setFilters: function(filters, disableInit)
           { //Set filters on page

               ui.clearer();

               for (filter in filters)
               {
                   switch (filter)
                   {
                       case "property":

                       break;

                       case "order1":

                       break;

                       case "order2":

                        break;

                       case "sort1":

                       break;

                       case "sort2":

                        break;

                       default:
                           if (!ui.filters.hasOwnProperty(filter))
                                 break;

                           for (i in filters[filter])
                           {
                               $('<input type="hidden" />').attr({
                                   name: 'filter[' + filter + '][]',
                                   value: filters[filter][i].id,
                                   class: 'filter-item'
                               }).data('text', filters[filter][i].text).appendTo(ui.filter_form);
                           }
                        break;
                   }
               }

               if (!disableInit)
                    ui.initFilters()
           },

           requester: function(url, params, pagination) {//get content from the server

                if (ui.loading != null)
                    ui.loading.abort();

                $(ui.container).html(ui.loader);
                ui.clearer();

               if (!pagination)
                    url = url.replace(/page[0-9]*\/$/i, '');

                history = url

                if (params)
                    history = history + '?' + params;

                History.pushState(null, null, history);
                $(document).trigger(ui.signals['start_load']);



                return  $.get(url, params, function(data) {
                    $(document).trigger(ui.signals['end_load'], [url, data]);
                }, 'json');
           }
       };


var uiDetail = {
        tabs: ".cpn-details-tab",

        loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',



        tabContent: '.tpp-dt-content',

        init: function () {
            tabs = $(uiDetail.tabs);

            if (tabs.length == 0)
                return false;

            tabs.tabs({
                beforeLoad: function(event, ui) {
                    uiDetail.setLoader(ui.panel);
                },
                load: uiDetail.cacheData
            });

            $(document).on('click', uiDetail.tabContent + ' .panging a', uiDetail.pageNav);
        },

        setLoader: function (content) {
            content.html(uiDetail.loader);
        },

        cacheData: function( event, ui ) {
            var tabLink = ui.tab.find('a');
            var id = tabLink.data('id');
            var tab = $('<div></div>').attr('id', id).append(ui.panel);

            tabLink.attr('href', '#' + id);
            $(this).append(tab);
        },

        pageNav: function() {
            var content = $(this).parents(uiDetail.tabContent).parent();
            var link = $(this).attr('href');
            uiDetail.setLoader(content);
            content.load( link );

            return false;
        }
};