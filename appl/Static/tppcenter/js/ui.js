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
            curPage: null,
            scripts: [],
            styles: [],

           filters: {

               country: {
                   selector: '#filter-country',
                   name: 'filter[country][]' //hidden input name
               },

               tpp: {
                   selector: '#filter-tpp',
                   name: 'filter[tpp]' //hidden input name
               }
           },


            signals: {
                start_load: 'startPageLoad',
                end_load: 'pageLoaded',
                link_click: 'linkClicked',
                scripts_loaded: 'scriptsLoaded'
            },

            init: function() {
                ui.curPage = $('.cur-page');
                ui.keywords = $('.keyword .list-key');
                ui.filter_form = $('form[name="filter-form"]');

                ui.initFilters();

                $(document).bind(ui.signals['end_load'], ui.loadScripts);
                $(document).bind(ui.signals['scripts_loaded'], ui.setPage);

                $(document).on('click', '.single-page', ui.onClick);
            },

            initFilters: function() {

                for (filter in ui.filters)
                {
                    if (!options.hasOwnProperty(filter))
                        continue;

                    data = []

                    $('input[name="filter[' + filter + '][]"').each(function() {
                        data.push({'id': $(this).val(), 'text': $(this).data('text')});
                    });

                    options[filter]['data'] = data;

                    field = $(ui.filters[filter].selector).data('name', filter);
                    field.select2(options[filter]);

                    field.on("change", function (e) { filterChange($(this).data('name'), e)});
                }
            },

            onClick: function() {
                $(document).trigger(ui.signals.link_click, $(this));

                url = $(this).attr('href');
                text = $(this).text();
                ui.curPage.text(text);

                ui.loading = ui.requester(url);

                return false;
            },

            loadScripts: function(event, url, data) {
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

                $.getScript(scripts);

                setTimeout(function() {
                    $(document).trigger(ui.signals['scripts_loaded'], [data['content']])
                }, 500);
            },

            setPage: function(event, content){

                $(ui.container).replaceWith( content );
            },

            clearer: function() {
                ui.filter_form.find('input[name]').remove();
                ui.keywords.html('');
            },

           setFilters: function(filters)
           {
               for (filter in filters)
               {
                   switch (filter)
                   {
                       case "property":

                       break;

                       case "sort1":

                       break;

                       case "sort2":

                        break;

                       case ui.filters.hasOwnProperty(filter):
                           for (i in filters[filter])
                           {
                               $('<input type="hidden" />').attr({
                                   name: 'filter[' + filter + '][]',
                                   value: filters[filter][i].id
                               }).data('text', filters[filter][i].text).appendTo(ui.filter_form);
                           }
                        break;
                   }
               }

               ui.initFilters()
           },

           requester: function(url, params) {

                if (ui.loading != null)
                    ui.loading.abort();

                $(ui.container).html(ui.loader);
                ui.clearer();

                history = url

                if (params)
                    history = history + '?' + params;

                History.pushState(null, null, history);

                $(document).trigger(ui.signals['start_load']);

                return  $.get(url, params, function(data) {
                    $(document).trigger(ui.signals['end_load'], [url, data]);
                }, 'json')
           }
       }

