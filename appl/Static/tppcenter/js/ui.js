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
            curPage: null,
            scripts: [],
            styles: [],

            signals: {
                start_load: 'startPageLoad',
                end_load: 'pageLoaded',
                link_click: 'linkClicked',
                scripts_loaded: 'scriptsLoaded'
            },

            init: function() {
                ui.curPage = $('.cur-page');
                ui.keywords = $('.keyword .list-key');
                ui.setScriptsStyles();
                $(document).bind(ui.signals['end_load'], ui.loadScripts);
                $(document).bind(ui.signals['scripts_loaded'], ui.setPage);

                $(document).on('click', '.single-page', ui.onClick);
            },

            setScriptsStyles: function() {
                $('script[src]').each(function() {
                    ui.scripts.push($(this).attr('src'));
                });

                $('link[href]').each(function() {
                    ui.styles.push($(this).attr('href'));
                });
            },

            onClick: function() {

                url = $(this).attr('href');
                text = $(this).text()
                ui.curPage.text(text)

                ui.loading = ui.requester(url)

                return false
            },

            loadScripts: function(event, url, data) {
                var head = $('head');

                styles = data['styles']
                scripts = data['scripts']

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

            requester: function(url, params) {

                if (ui.loading != null)
                    ui.loading.abort();

                $(ui.container).html(ui.loader)
                ui.keywords.html('')

                history = url

                if (params)
                    history = history + '?' + params

                History.pushState(null, null, history)

                $(document).trigger(ui.signals['start_load'])

                return  $.get(url, params, function(data) {
                    $(document).trigger(ui.signals['end_load'], [url, data])
                }, 'json')
            }
        }

