var ContentManager = (function() {
    var content_holder;
    var loader;
    var requests = {};

    function init() {
        content_holder = $('#content');
        loader = $('#loader');
    }

    function fetchAdv() {
        //TODO
    }

    function fetchContent(href) {
        content_holder.hide();
        loader.show();

        requests['content'] = $.ajax(href, {
            beforeSend: function() {
                if(requests['content']) {
                    try {
                        requests['content'].abort();
                    } catch(e) { alert('catch error TODO remove'); }
                }
            },
            context: content_holder,
            success: function( response ) {
                $(this).html(response);
                loader.hide();
                content_holder.show();
            },
            async: true,
            dataType: 'html',
        });
    }

    return {
        init: init,
        fetchContent: fetchContent
    }
})();

var SinglePage = (function() {
    var history;

    function init() {
        $(document).on('click', 'a.single-page', handler);
        history = History.createBrowserHistory();
        history.listen(function() {
            var href = location.pathname + location.search;
            ContentManager.fetchContent(href);
        });
    }

    function handler(event) {
        var pageRef = $(this).attr('href');

        if (isModifiedEvent(event) || !isLeftClickEvent(event)) {
          return;
        }

        if (event.defaultPrevented === true) {
          return;
        }

        event.preventDefault( );
        push(pageRef);
    }

    function isLeftClickEvent(event) {
      return event.button === 0;
    }

    function isModifiedEvent(event) {
      return !!(event.metaKey || event.altKey || event.ctrlKey || event.shiftKey);
    }

    function push(href) {
        history.push(href);
    }

    return {
        init: init
    }

})();



