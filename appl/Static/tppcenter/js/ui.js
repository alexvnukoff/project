/**
 * Created by user on 19.02.14.
 */


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
                   name: 'filter[country]' //hidden input name
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
                scripts_loaded: 'scriptsLoaded',
                filter_removed: 'filterRemoved'
            },

            init: function() {
                ui.curPage = $('.cur-page');
                ui.keywords = $('.keyword .list-key');
                ui.filter_form = $('form[name="filter-form"]');

                ui.initFilters();

                $(document).bind(ui.signals['end_load'], ui.loadScripts);
                $(document).bind(ui.signals['scripts_loaded'], ui.setPage);
                $(document).bind(ui.signals['filter_removed'], ui.filterPageLoad);

                $(document).on('click', '.single-page', ui.onClick);
                $(document).on('click', '.filter-remove', ui.onRemove);
                $(document).on('click', '#save-filter', ui.filterPageLoad);
                $(document).on('click', '.panging a', ui.pageNav);
            },

            pageNav: function() {

                url = $(this).attr('href');

                ui.requester(url, '', true);

                return false;
            },

            filterPageLoad: function() {
                var params = ui.filter_form.serialize();
                $(".filter-form, #fade-profile").hide();

                ui.requester(window.location.pathname, params)
            },

            onRemove: function() {

                link = $(this).parent()
                id = link.data('id');
                ui.filter_form.find('input[value="' + id + '"].filter-item').remove();
                link.parent().remove();

                //ui.initFilters();
                $(document).trigger(ui.signals.filter_removed);

            },

            initFilters: function() {//initial values for filter popup
                var filter_keys = []

                for (filter in ui.filters)
                {
                    if (!options.hasOwnProperty(filter))
                        continue;


                    field = $(ui.filters[filter].selector).data('name', filter);
                    field.select2(options[filter]);

                    var data = []

                    if (filter == 'country')
                    {
                        $('input[name="filter[' + filter + '][]"].filter-item').each(function() {
                            data.push($(this).val());
                            filter_keys.push({id: $(this).val(), title: $(this).data('text')});
                        });

                        if (data.length > 0)
                            field.select2('val', data);
                        else
                            field.select2('val', '');
                    }
                    else
                    {
                        $('input[name="filter[' + filter + '][]"].filter-item').each(function() {
                            data.push({id: $(this).val(), title: $(this).data('text')});
                            filter_keys.push(data[data.length - 1]);
                        });

                        if (data.length > 0)
                        {
                            field.select2('data', data);
                        }
                        else
                        {
                            $(ui.filters[filter].selector).select2('val', '');
                        }
                    }

                    field.on("change", function (e) { filterChange($(this).data('name'), e)});

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
            },

            clearer: function() { //clear all filters
                ui.filter_form.find('input[name].filter-item').remove();
                //ui.keywords.html('');
            },

           setFilters: function(filters)
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
       }

