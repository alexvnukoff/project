/**
 * Created by user on 19.02.14.
 */

var ui =
{ //One-Page site ui script (including filters + adv)
    loading: null,
    loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',
    container: ".news-center .container",
    keywords: null,
    filter_form: null,
    search_form: null,
    curPage: null,
    scripts: [],
    styles: [],

    bann:
    {
        right: null,
        left: null
    },

    tops: null,

    filters:
    { //filters selectors + field names
        country:
        {
            selector: '#filter-country',
            name: 'filter[country]'
        },

        tpp:
        {
            selector: '#filter-tpp',
            name: 'filter[tpp]'
        },
        company:
        {
            selector: '#filter-company',
            name: 'filter[company]'
        },
        bp_category:
        {
            selector: '#filter-bp_category',
            name: 'filter[bp_category]'
        },
        branch:
        {
            selector: '#filter-branch',
            name: 'filter[branch]'
        }
    },

    signals:
    {
        start_load: 'startPageLoad', //Before requesting the page from server
        end_load: 'pageLoaded', //Got the data from the server(scripts not loaded yet)
        link_click: 'linkClicked', //Menu link just clicked
        scripts_loaded: 'scriptsLoaded', // CSS + JS already loaded
        filter_removed: 'filterRemoved' //Filter removed from filter bar / search bar
    },

    init: function()
    {
        ui.curPage = $('.cur-page');
        ui.keywords = $('.keyword .list-key');
        ui.filter_form = $('form[name="filter-form"]');
        ui.search_form = $('form[name="search"]');

        if (ui.filter_form.length == 0)
            return false;

        //Set filter from query string
        ui.initFilters();
        ui.initMenu();

        //Custom events
        $(document).bind(ui.signals['end_load'], ui.loadScripts);
        $(document).bind(ui.signals['scripts_loaded'], ui.setPage);
        $(document).bind(ui.signals['filter_removed'], ui.filterPageLoad);

        //JS events
        $(document).on('click', '.single-page', ui.onClick);
        $(document).on('click', '.filter-remove', ui.onRemove);
        $(document).on('click', '#save-filter', ui.saveFilter);
        $(document).on('click', ui.container + ' .panging a', ui.pageNav);
        $(document).on('click', '.tab1-cate > li', ui.setSelectedMenu);
        $(document).on('submit', 'form[name="search"]', ui.search);
    },

    search: function()
    { //On search request

        //Search condition
        var val = $(this).find('input[name="q"]').val();

        //Clear search or search when search condition length is more than 3 symbols
        if (val.length > 0 && val.length < 3)
            return false;

        //Update query string (needed when we already have old search condition)
        url = updateURLParameter("q", val);

        //remove host + path from the new url
        params = url.replace(window.location.origin + window.location.pathname, '');

        //Search request , substr used to ignore the leading "?" symbol
        ui.requester(window.location.pathname, params.substr(1));

        return false;
    },

    pageNav: function()
    { //Live pagination handler

        url = $(this).attr('href');

        ui.requester(url, '', true);

        return false;
    },

    saveFilter: function()
    { //Apply filters

        var filters = {};

        for (filter in ui.filters)
        {
            field = $(ui.filters[filter].selector);

            //No filter selector on the popup for this type of item
            if (field.length == 0)
                continue;

            //Get filter values for this type of item
            var values = field.select2('data');

            if (values && values.length > 0)
            {//if filter exists add to filter object
                filters[filter] = values;
            }
        }

        ui.setFilters(filters, true);

        $(".filter-form, #fade-profile").hide();

        ui.filterPageLoad();
    },

    filterPageLoad: function()
    { //Load filtered date including search condition
        var params = ui.filter_form.serialize();
        var search = ui.search_form.serialize();

        if (params != '')
            params += '&' + search;
        else
            params = search;

        ui.requester(window.location.pathname, params)

    },

    onRemove: function()
    { //Filter removed from filter bar / search bar

        link = $(this).parent();
        id = link.data('id');

        //remove the filter from the form
        ui.filter_form.find('input[value="' + id + '"].filter-item').remove();

        link.parent().remove();

        $(document).trigger(ui.signals.filter_removed);
    },

    initFilters: function()
    {//initial values for filter popup
        var filter_keys = [];

        for (filter in ui.filters)
        {//Init filters in select2 fields form the form hidden fields
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

    initMenu: function() {
        var pathname = window.location.pathname;
        pathname = pathname.substring(1, pathname.length - 2).split('/')

        if (pathname.length == 2 && pathname[1] == 'my')
        {
            url = pathname;
        } else {
            url = pathname[0]
        }

        $('.tab1-cate > li > a[href="/' + url + '/"]').parent().addClass('selected-menu');
    },

    setSelectedMenu: function() {

        $('.tab1-cate > li.selected-menu').removeClass('selected-menu');
        $(this).addClass('selected-menu');
    },

    setKeyFilters: function(data)
    { //Removable filters
        keys = ''

        if (data.length > 0)
        {
            for(i=0, len = data.length - 1; i < 5; i++)
            {//Set 5 random selected filters to filter bar / search bar
                keys += '<li>' + data[i].title + '<a href="#" data-id="' + data[i].id + '">' +
                            '<i class="i-close filter-remove imgnews"></i></a></li>';

                if (len == i) // if there is less then 5 filters selected
                    break
            }
        }

        ui.keywords.html(keys);
    },

    onClick: function()
    { //On menu click
        $(document).trigger(ui.signals.link_click, $(this));

        ui.search_form.find('input[name="q"]').val('');

        var url = $(this).attr('href');

        ui.loading = ui.requester(url);

        return false;
    },

    loadScripts: function(event, url, data, history)
    { //load addition scripts
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

        setTimeout(function() {//Wait 500 ms untill css MAY be loaded
            $(document).trigger(ui.signals['scripts_loaded'], [data])
        }, 500);
    },

    setPage: function(event, data)
    {//Put the loaded html on the screen
        ui.setFilters(data.filters);

        $(ui.container).replaceWith( data.content );
        var addBtn = $('.add-new');



        if ( !addBtn.hasClass('logged-out')) {
            var imgBtn = addBtn.find('.btn-fil');

            if ( data.addNew != '' ) {
               imgBtn.removeClass('disable');
               addBtn.attr('href', data.addNew);

            } else {
               addBtn.attr('href', '#');
               imgBtn.addClass('disable');
            }
        }

        if ( data.current_section ) {
            $('title').text(data.current_section);
        }

        ui.filter_form = $('form[name="filter-form"]');
        ui.initFilters();
    },

    clearer: function()
    { //clear all filters
        ui.filter_form.find('input[name].filter-item').remove();
    },

    setFilters: function(filters, disableInit)
    { //Set hidden inputs containing filters to form

        ui.clearer();

        for (filter in filters)
        {
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

        }

        if (!disableInit)
            ui.initFilters()
    },

    getAdvTop: function(params)
    {//Async load adv tops when the page was loaded

        if (ui.tops != null)
            ui.tops.abort();

        ui.tops = $.ajax('/adv/tops/', {
            data: params,
            type: "GET",
            success: function(data) {
                ui.tops = null;
                $('.news-ads-wrapper').replaceWith(data);
            },
            cache: false,
            dataType: 'html'
        });
    },

    getAdvBanners: function(params)
    {//Async load banners when the page was loaded

        var url = '/adv/bann/';

        if (ui.bann.left != null)
            ui.bann.left.abort();

        if (ui.bann.right != null)
            ui.bann.right.abort();

        places =
        {
            right: ["Right 1", "Right 2"],
            left: ["Left 1", "Left 2", "Left 2"]
        };

        ui.bann.left = $.ajax(url + '?' + params, {
            data: {
                places: places.left
            },
            type: "POST",
            success: function(data) {
                ui.bann.left = null;
                $('.banner-wrapper-left').html(data);
            },
            cache: false,
            dataType: 'html',
            async: true
        });

        ui.bann.right = $.ajax(url + '?' + params, {
            data:
            {
                places: places.right
            },
            type: "POST",
            success: function(data)
            {
                ui.bann.right = null;
                $('.banner-wrapper-right').html(data);
            },
            cache: false,
            dataType: 'html',
            async: true
        });
    },

    requester: function(url, params, pagination)
    {//get content from the server

        if (ui.loading != null)
            ui.loading.abort();

        $(ui.container).html(ui.loader);
        ui.clearer();

        if (!pagination)
            url = url.replace(/page[0-9]*\/$/i, '');

        var history = url;

        if (params)
            history = history + '?' + params;

        History.pushState(null, null, history);
        $(document).trigger(ui.signals['start_load']);

        ui.getAdvBanners(params);
        ui.getAdvTop(params);

        return $.ajax(url, {
            data: params,
            type: "GET",
            success: function(data) {
                ui.loading = null;
                $(document).trigger(ui.signals['end_load'], [url, data, history]);
            },
            cache: false,
            dataType: 'json'
        });
    }
};


var uiDetail =
{// Detail page tabs
    tabs: ".cpn-details-tab",

    loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',

    tabContent: '.tpp-dt-content',

    init: function()
    {
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

    setLoader: function (content)
    {//Set loader gif
        content.html(uiDetail.loader);
    },

    cacheData: function( event, ui )
    {//Not load the tab again if was already loaded
        var tabLink = ui.tab.find('a');
        var id = tabLink.data('id');
        var tab = $('<div></div>').attr('id', id).append(ui.panel);

        tabLink.attr('href', '#' + id);
        $(this).append(tab);
    },

    pageNav: function()
    { //Pagination in tabs
        var content = $(this).parents(uiDetail.tabContent).parent();
        var link = $(this).attr('href');

        uiDetail.setLoader(content);
        content.load( link );

        return false;
    }
};

var messagesUI = {

    curChat: 'mess-cur' ,
    chatList: '.message-tabcontent',
    messageLine: '.customline',
    messageBox: '.custom-contentin',
    messageList: '.message-list',
    textarea: '#message-box-',
    chatWindow: 'custom-content-',
    messagesLoader: null,


    onScrollTop: function( el )
    {//Load older messages when scrolled to top

        el.unbind( 'scroll' );

        if ( el.find( '.last' ).length )
            return true;

        var active_id = $( '.' + messagesUI.curChat + ' a' ).data( 'user-id' );

        el.find( '.dateline:first' ).replaceWith( '<div class="message-paging-loader">' +
                                                        '<img class="im-test" src="/static/tppcenter/img/messages-loader.gif" />' +
                                                    '</div>' );

        var last_message = el.find( messagesUI.messageLine + ':first' );
        var date = last_message.data( 'date' );
        var lid =  last_message.data( 'message' );
        var url = '/messages/' + active_id + '/';

        $.ajaxQueue({//Add the request to queue
            url: url,
            data: {
                type: 'scroll',
                lid: lid,
                date: date
            },

            success: function(data)
            {
                messagesUI.bindScroll();
                el.find( '.message-paging-loader' ).replaceWith( data );
            },
            type: 'GET'
        });
    },

    bindScroll: function()
    {//Set listener for scroll event on the message list holder

        $( messagesUI.messageBox ).unbind( 'scroll' );

        $( messagesUI.messageBox + ':visible' ).bind( 'scroll', function() {

            if( $(this).scrollTop() == 0 )
                messagesUI.onScrollTop( $(this) );
        });
    },

    scroollMessageDown: function()
    {//Scroll the message holder last message
        var active_id = $( '.' + messagesUI.curChat + ' a' ).data( 'user-id' );
        var content = $( messagesUI.messageBox + ':visible' );
        var content2 = $( '#custom-content-'+ active_id );
        var height = content2.find( messagesUI.messageList ).height();

        content.scrollTop( height );

    },

    sendMessage: function()
    {
        var active_id = $( '.' + messagesUI.curChat + ' a' ).data( 'user-id' );

        if ( !active_id )
            return false;

        var textarea = $( messagesUI.textarea + active_id );
        var val = textarea.val();

        if ( val == '' ) //prevent sending empty message
            return false;

        textarea.attr( 'disabled', 'disabled' );

        $.ajaxQueue({

            url: '/messages/add/',
            data: {
                text: val,
                active: active_id
            },

            success: function( data ) {

                messagesUI.getMessages( active_id );
                textarea.val( '' );
                textarea.removeAttr( 'disabled' );
                messagesUI.scroollMessageDown();
                messagesUI.bindScroll()

            },

            type: 'POST'
        });

           return false;

    },

    getMessages: function( coll ) {
            var selector = $( '#' + messagesUI.chatWindow + coll );

            if ( selector.length == 0 )
                return false;

            var lastTime = selector.find( messagesUI.messageLine + ':last' ).data( 'date' );
            var lid = selector.find( messagesUI.messageLine + ':last' ).data( 'message' );
            var url = '/messages/' + coll + '/';

            jQuery.ajaxQueue({

                url: url,
                data: {
                    date: lastTime,
                    lid: lid
                },

                success: function( data ) {

                    selector.find( messagesUI.messageList ).append( data );
                    messagesUI.scroollMessageDown();
                    messagesUI.bindScroll()



                },

                dataType: 'html',
                type: 'GET'
            });
    },

    getMessageBox: function( coll, newPanel ) {

            var url = '/messages/' + coll + '/';
            var content = ''

            History.pushState( null, null, url );

            jQuery.ajaxQueue({

                url: url,
                data: {box: 1},

                success: function( data ) {

                    newPanel.html( data );
                    messagesUI.scroollMessageDown();
                    messagesUI.bindScroll()

                },

                dataType: 'html',
                type: 'GET'
            });
    },

    onSelectRecipient: function() {

        var container = $(this).parent();

        if ( container.hasClass(messagesUI.curChat) )
            return false;

        var loadUrl = $(this).data('url');
        var recipientID = $(this).data('user-id');
        var messages = $('#custom-content-' + recipientID);
        var old = $(messagesUI.chatList + ' .' + messagesUI.curChat)


        $('#unread-'+recipientID).text("");

        if ( old.length > 0 )
        {
            old.removeClass(messagesUI.curChat);
            oldID = old.find('a').data('user-id');
            $('#custom-content-' + oldID).hide();
        }

        container.addClass(messagesUI.curChat);


        if ( messages.length > 0)
        {
            messages.show();
        } else {
            messagesUI.messagesLoader.show();
            History.pushState( null, null, loadUrl);

            var jqxhr = $.get( loadUrl, 'box=1', function(data) {
                messagesUI.messagesLoader.hide();
                $('.custom-content:last').after(data);
                messagesUI.scroollMessageDown();



            });
        }



        return false;
    },


    init: function() {
        $( ".messages-l" ).tabs();

        messagesUI.messagesLoader = $('.message-loader');

        $(messagesUI.chatList).on('click', 'li a', messagesUI.onSelectRecipient);


            /*
            $( messagesUI.chatList ).tabs({

                beforeLoad: function( event, ui ) {
                    ui.panel.html();
                },

                load: function( event, ui ) {

                    var tabLink = ui.tab.find( 'a' );
                    var id = tabLink.data( 'user-id' );
                    var tab = $( '<div></div>' ).attr( 'id', messagesUI.chatWindow + id ).append( ui.panel );

                    tabLink.attr( 'href', '#' + messagesUI.chatWindow + id );

                    $(this).append( tab );

                    messagesUI.scroollMessageDown();
                    messagesUI.bindScroll();
                },

                activate: function( event, ui) {

                    var url = ui.newTab.find( 'a' ).data( 'url' );

                    History.pushState( null, null, url);

                    $( messagesUI.chatList + " ." + messagesUI.curChat ).removeClass( messagesUI.curChat )
                    ui.newTab.addClass( messagesUI.curChat );
                }
            });
            */



        $(document).on( 'click', 'a.send-message', messagesUI.sendMessage );

        $(document).bind( 'new_message', function( ev, fromUser ) {

            var active_id = $( '.' + messagesUI.curChat  + ' a').data('user-id');

            if ( fromUser == active_id )
                messagesUI.getMessages( active_id );
        });

        messagesUI.scroollMessageDown();
        messagesUI.bindScroll();

    }
};

uiEvents = {

    loader: '<li class="event-loader"><img src="/static/tppcenter/img/messages-loader.gif" /></li>',
    type: null,
    holder: null,
    form: null,
    contentBox: null,
    num: 0,
    numHolder: null,
    boxParent: null,



    init: function() {
        $(".showevent").click(uiEvents.showEventBox);
    },

    showEventBox: function() {
        uiEvents.holder = $(this).parents('.event-holder');
        uiEvents.form = uiEvents.holder.find('.formevent');
        uiEvents.contentBox = uiEvents.form.find('ul');
        uiEvents.boxParent = uiEvents.contentBox.parent();
        uiEvents.numHolder = uiEvents.holder.find('.num');
        var content = uiEvents.form.find('li');
        var first = 0;

        if ( content.length > 0 ) { //Some content already loaded

            uiEvents.num = parseInt(uiEvents.numHolder.text());

            if ( uiEvents.num == 0 )
            {
                uiEvents.form.show();
                uiEvents.bindScroll( $(this) );

                return false

            }

            first = content.first().data('id');
        }

        uiEvents.type = uiEvents.form.attr('id'); //event type
        uiEvents.contentBox.prepend(uiEvents.loader);

        uiEvents.form.show();

        uiEvents.requester({first: first, type: uiEvents.type});

        return false;
    },

    requester: function(data) {

        $.get('/notification/get/', data, function(data) {
            uiEvents.contentBox.find('li.event-loader').replaceWith(data.data);

            if ( uiEvents.num > 0 )
            {
                if ( uiEvents.num > data.count )
                    uiEvents.num = 0;
                else
                    uiEvents.num = uiEvents.num - data.count;

                uiEvents.numHolder.text(uiEvents.num);
            }
            uiEvents.bindScroll();
        }, 'json');
    },

    onScrollDown: function( el ) {
        uiEvents.boxParent.unbind( 'scroll' );

        var last = uiEvents.boxParent.find('ul li:last').data('id');

        uiEvents.contentBox.append(uiEvents.loader);

        uiEvents.requester({type: uiEvents.type, last: last});

    },

    bindScroll: function() {

        uiEvents.boxParent.unbind( 'scroll' );

        if ( uiEvents.contentBox.find('.last').length > 0 )
            return false;


        var top = uiEvents.contentBox.height() - uiEvents.boxParent.height();


        uiEvents.boxParent.bind( 'scroll', function() {

            if( uiEvents.boxParent.scrollTop() == top )
                uiEvents.onScrollDown();
        });
    }
};

var galleryUpload = { //Async gallery uploader (uploadify)

    options : {
        uploadLimit: 20,
        height   : 105,
        width    : 110,
        auto     : true,
        queueID  : 'queue'
    },

    loadURL: '/',
    structureURL: '/',
    loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',

    fail_upload : '',

    lang : {
        uploading: '',
        success: '',
        fail: '',
        wasUploaded: ''
    },

    init : function(lang, swf, image, upload_url, loadURL, structureURL)
    {
        galleryUpload.lang = lang;

        galleryUpload.options['formData'] = {
            csrfmiddlewaretoken : getCookie('csrftoken')
        };
        galleryUpload.options['swf'] = swf;
        galleryUpload.options['uploader'] = upload_url;
        galleryUpload.options['buttonImage'] = image;
        galleryUpload.options['itemTemplate'] = galleryUpload.getQueueTemplate();
        galleryUpload.options['onUploadError'] = galleryUpload.onUploadError;
        galleryUpload.options['onQueueComplete'] = galleryUpload.onQueueComplete;
        galleryUpload.options['onUploadSuccess'] = galleryUpload.onUploadSuccess;
        galleryUpload.options['onUploadStart'] = galleryUpload.onUploadStart;

        galleryUpload.loadURL = loadURL;
        galleryUpload.structureURL = structureURL;

        $(document).on("click", ".removePhoto", galleryUpload.removePhoto);


        $('#file_upload').uploadify(galleryUpload.options);

    },

    getQueueTemplate : function() {
        return '<div id="${fileID}" class="uploadify-queue-item">' +
                '<span class="fileName"><strong>' + galleryUpload.lang.uploading + '</strong>: ${fileName} (${fileSize})...' +
                '</span></div>';
    },

    onUploadSuccess : function(file, data) {
        var queue = $('#' + file.id);

        queue.find('span').append( ' - ' + galleryUpload.lang.success );
        queue.css('color', 'green');

        //$('.tpp-gallery').prepend(data);
    },

    onUploadError : function(file) {
        var queue = $('#' + file.id);

        galleryUpload.fail_upload += file.name + "\r\n";

        queue.find('span').append(' - ' + galleryUpload.lang.fail );
        queue.css({color: 'red', fontWeight: 'bold'});
    },

    onQueueComplete : function(queueData) { //Show all failed uploads

        if ( queueData.uploadsErrored > 0 )
        {
            alert( galleryUpload.lang.wasUploaded + ":\r\n" + galleryUpload.fail_upload );
        }

        $('.galleryHolder').load(galleryUpload.structureURL);

        galleryUpload.fail_upload = '';
    },

    onUploadStart: function() {
        $('.galleryHolder').html(galleryUpload.loader);
    },

    removePhoto: function() {
        var link = $(this).attr("href");
        $('.galleryHolder').html(galleryUpload.loader);

        $.get(link, function(data) {
            $('.galleryHolder').load(galleryUpload.structureURL);
        });
        
        return false;
    }
};
