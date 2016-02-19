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
        countries:
        {
            selector: '#filter-countries',
            name: 'filter[countries]'
        },
        chamber:
        {
            selector: '#filter-chamber',
            name: 'filter[chamber]'
        },
        organization:
        {
            selector: '#filter-organization',
            name: 'filter[organization]'
        },
        company:
        {
            selector: '#filter-company',
            name: 'filter[company]'
        },
        bp_categories:
        {
            selector: '#filter-bp_categories',
            name: 'filter[bp_categories]'
        },
        b2b_categories:
        {
            selector: '#filter-b2b_categories',
            name: 'filter[b2b_categories]'
        },
        b2c_categories:
        {
            selector: '#filter-b2c_categories',
            name: 'filter[b2c_categories]'
        },
        branches:
        {
            selector: '#filter-branches',
            name: 'filter[branches]'
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
	    ui.initMenu();
        ui.curPage = $('.cur-page');
        ui.keywords = $('.keyword .list-key');
        ui.filter_form = $('form[name="filter-form"]');
        ui.search_form = $('form[name="search"]');

        if (ui.filter_form.length == 0)
            return false;

        //Set filter from query string
        ui.initFilters();

        //Custom events
        $(document).bind(ui.signals['end_load'], ui.loadScripts);
        $(document).bind(ui.signals['scripts_loaded'], ui.setPage);
        $(document).bind(ui.signals['filter_removed'], ui.filterPageLoad);

        //JS events
        $(document).on('click', '.single-page', ui.onClick);
        $(document).on('click', '.filter-remove', ui.onRemove);
        $(document).on('click', '#save-filter', ui.saveFilter);
        $(document).on('click', ui.container + ' .panging a', ui.pageNav);
        $(document).on('click', '.tab1-cate > li a', ui.setSelectedMenu);
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
        filter_key = link.data('type')

        //remove the filter from the form
        ui.filter_form.find('input[value="' + id + '"][name="filter[' + filter_key + '][]"].filter-item').remove();

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
                data.push({id: $(this).val(), title: $(this).data('text'), filter_key: filter});
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
        pathname = pathname.substring(1, pathname.length - 1).split('/');

        var url = '/'

        if (pathname.length == 2 && pathname[1] == 'my')
        {
            url = pathname.join('/');
        } else {
            url = pathname[0]
        }

        $('.tab1-cate > li > a[href="/' + url + '/"]').addClass('selected-menu');
    },

    setSelectedMenu: function() {

        $('.tab1-cate > li a.selected-menu').removeClass('selected-menu');
        $(this).addClass('selected-menu');
    },

    setKeyFilters: function(data)
    { //Removable filters
        keys = '';

        if (data.length > 0)
        {
            for(i=0, len = data.length - 1; i < 5; i++)
            {//Set 5 random selected filters to filter bar / search bar
                keys += '<li>' + data[i].title + '<a href="#" data-id="' + data[i].id + '" data-type="' + data[i].filter_key + '">' +
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
        var addBtn = $('.addButton');



        if ( !addBtn.hasClass('logged-out')) {
            if ( data.addNew != '' ) {
               addBtn.removeClass('disable');
               addBtn.parent().attr('href', data.addNew);

            } else {
               addBtn.parent().attr('href', '#');
               addBtn.addClass('disable');
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
                                                        '<img class="im-test" src="/static/b24online/img/messages-loader.gif" />' +
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

    loader: '<li class="event-loader"><img src="/static/b24online/img/messages-loader.gif" /></li>',
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

var FileUploader = { //Async uploader (uploadify)

    options : {
        fileSizeLimit: '100KB',
        uploadLimit: 5,
        // Button size
        height   : 105,
        width    : 110,
        auto     : true,
        successTimeout: 60,
        queueID  : 'queue'
    },

    loadURL: '/',
    structureURL: '/',
    loader: '<div class="loader"><img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/></div>',
    parent: null,
    fail_upload : '',

    lang : {
        uploading: '',
        success: '',
        fail: '',
        wasUploaded: ''
    },

    init : function(input, lang, loadURL, structureURL, options)
    {
        FileUploader.lang = lang;

        FileUploader.options['formData'] = {
            csrfmiddlewaretoken : getCookie('csrftoken')
        };

        jQuery.extend(FileUploader.options, options);

        FileUploader.options['itemTemplate'] = FileUploader.getQueueTemplate();
        FileUploader.options['onUploadError'] = FileUploader.onUploadError;
        FileUploader.options['onQueueComplete'] = FileUploader.onQueueComplete;
        FileUploader.options['onUploadSuccess'] = FileUploader.onUploadSuccess;
        FileUploader.options['onUploadStart'] = FileUploader.onUploadStart;

        FileUploader.loadURL = loadURL;
        FileUploader.structureURL = structureURL;

        FileUploader.parent = input.parents('.tpp-dt-content');
        FileUploader.parent.on("click", ".removePhoto", FileUploader.removePhoto);

        input.uploadify(FileUploader.options);

    },

    getQueueTemplate : function() {
        return '<div id="${fileID}" class="uploadify-queue-item">' +
                '<span class="fileName"><strong>' + FileUploader.lang.uploading + '</strong>: ${fileName} (${fileSize})...' +
                '</span></div>';
    },

    onUploadSuccess : function(file, data) {
        var queue = $('#' + file.id);

        queue.find('span').append( ' - ' + FileUploader.lang.success );
        queue.css('color', 'green');

        //$('.tpp-gallery').prepend(data);
    },

    onUploadError : function(file) {
        var queue = $('#' + file.id);

        FileUploader.fail_upload += file.name + "\r\n";

        queue.find('span').append(' - ' + FileUploader.lang.fail );
        queue.css({color: 'red', fontWeight: 'bold'});
    },

    onQueueComplete : function(queueData) { //Show all failed uploads

        if ( queueData.uploadsErrored > 0 )
        {
            alert( FileUploader.lang.wasUploaded + ":\r\n" + FileUploader.fail_upload );
        }

        FileUploader.parent.find('.files_holder').load(FileUploader.structureURL);

        FileUploader.fail_upload = '';
    },

    onUploadStart: function() {
        FileUploader.parent.find('.files_holder').html(FileUploader.loader);
    },

    removePhoto: function() {
        var link = $(this).attr("href");
        FileUploader.parent.find('.files_holder').html(FileUploader.loader);

        $.get(link, function(data) {
            FileUploader.parent.find('.files_holder').load(FileUploader.structureURL);
        });

        return false;
    }
};


var companyStructure =
{
    overlay: '#fade-profile',

    forms: {},

    structureURL: "",

    loader: '<div class="loader">' +
                '<img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/>' +
            '</div>',

    init: function(structureURL, LANG) {

        this.LANG = LANG;

        var self = this;

        self.structureURL = structureURL;
        self.overlay = $(this.overlay);

        self.setForms();
        self.subIcon();

        // mark Department row in Company-structure
        $('.sitemap > li a, .vacancy li').on('click', function() {
            return self.rowClick($(this))
		});

        $('#add-button').on('click', function() {
            return self.addNew($(this));
		});

        // edit Department or Vacancy (popup window)
        $('#edit-button').on('click', function () {
            return self.edit($(this))
        });

        // remove Department or Vacancy
        $('#remove-button').on('click', function() {
            return self.remove($(this));
		});
    },


    setForms: function() {

        var LANG = this.LANG;

        this.forms = {
            vacancy:
                '<div class="vacadd" id="add-vac-popup">' +
                    '<i class="close-formadd imgnews" />' +
                    '<div class="title">' + LANG['popup_vac_title'] + '</div>' +
                    '<div class="staffaddin">' +
                        '<label>' + LANG['popup_vac'] + '</label>' +
                        '<input type="text" name="" id="vac-name" class="textstructure" />' +
                        '<div class="formadd-button">' +
                            '<a class="btntype2" id="btn-add-vacancy" href="#">' + LANG['popup_ok'] + '</a>' +
                            '<a class="btntype1" href="#">' + LANG['popup_cancel'] + '</a>' +
                        '</div>' +
                    '</div>' +
                '</div>',


            departments:
                '<div class="staffadd" id="add-dep-popup">' +
                    '<i class="close-formadd imgnews" />' +
                    '<div class="title">' + LANG['popup_dep'] + '</div>' +
                    '<div class="staffaddin">' +
                        '<input type="text" name="" id="dep-name" class="textstructure" />' +
                        '<div class="formadd-button">' +
                            '<a class="btntype2" id="btn-add-depart" href="#">' + LANG['popup_ok'] + '</a>' +
                            '<a class="btntype1" href="#">' + LANG['popup_cancel'] + '</a>' +
                        '</div>' +
                    '</div>' +
                '</div>'
        }
    },

    subIcon: function() { // show or hide small arrows near the Department name
        var dep_lst = $('.sitemap li');
        dep_lst.each(function() {
            var vac_lst = $(this).find('li');
            if(vac_lst.size() == 0) {
                $(this).children('a').css('background', 'none');
            }
        });
    },

    toggleSub: function(link) {

        if (!link)
            return;

        var sub = link.parent().find(".sub");

        if (sub.is(":hidden")){
            sub.show();
            link.addClass('lesssitemap');
        } else {
            sub.hide();
            link.removeClass('lesssitemap');
        }
    },

    rowClick: function(clickedItem) {

        var link = null;

        if (!clickedItem.parent().hasClass('vacancy')) { //Department link click
            link = clickedItem;
            clickedItem = clickedItem.parent();
        }

        if (this.item)
        {
            this.item.removeClass('selected');

            if (this.item.data('item-id') == clickedItem.data('item-id')) {
                delete this.item;
                this.hidePanel();
                this.toggleSub(link);

                return false;
            }

        }


        clickedItem.addClass('selected');
        this.item = clickedItem;
        this.toggleSub(link);

        this.showPanel();
        return false;
    },

    showPanel: function() {
        $('.panel').show();
    },

    hidePanel: function() {
        $('.panel').hide();
    },

    addNew: function(clickedItem) {

        var action = "add";

        // If no row selected , department
        if(this.item) {
            this.setVacValues(action);
        } else {
            this.setDepValues(action);
        }

        return false;
    },

    edit: function(clickedItem) {
        var action = "edit";
        if (this.item) {
            if (!this.item.parent().hasClass('vacancy')) {
                this.setDepValues(action);
            } else {
                this.setVacValues(action);
            }
        }
        return false;
    },

    remove: function(clickedItem) {
        var contentHolder = $('#structure-tab .tpp-dt-content');

        if(this.item && confirm(this.LANG['confirm'])) {
            this.hidePanel();
            var id = this.item.data('item-id');
            var item_type = this.item.data('type');
            delete this.item;
            contentHolder.html(this.loader);

            $.post(this.structureURL, {id: id, "action": "remove", type: item_type}, function(data){
                contentHolder.replaceWith(data);
            }, 'html');
        }

        return false;
    },

    setOptions: function(select, options, selected_item) {
        select.find('option').remove();

        for (i in options) {
            obj = options[i];
            is_selected = (typeof selected_item !== "undefined" && obj.value == selected_item) ? 'selected' : '';
            select.append('<option value="' + obj.value + '" ' + is_selected + '>' + obj.name + '</option>');
        }
    },

    setDepValues: function(action) {
        var self = this;

        var form = $(self.forms.departments);
        var input = form.find('#dep-name');

        if (action == 'edit') {//edit
            input.val(self.item.find('a').text().trim());
        }

        // press Add button
	    form.on('click','#btn-add-depart', function() {
            var name = input.val().trim();

            if (!name)
                return false;

            var id = null;

            if (self.item)
                id = self.item.data('item-id');

            var contentHolder = $('#structure-tab .tpp-dt-content');
            contentHolder.html(self.loader);


            $.post(self.structureURL,{ name: name, id: id, action: action, type: 'department'}, function(data) {
                contentHolder.replaceWith(data);
            }, 'html');

            self.hideOverlay();

            return false;
		});

        <!-- press Cancel button -->
	    form.on('click','.btntype1', function() {
            self.hideOverlay();
            return false;
		});

        this.showOverlayForm(form);
    },

    setVacValues: function(action) {
        var self = this;

        if (!self.item)
            return false;

        var form = $(self.forms.vacancy);
        var input = form.find('#vac-name');

        if (action == 'edit') {//edit
            input.val(self.item.text().trim());
        }

        form.on('click','#btn-add-vacancy', function() {
            var name = input.val().trim();
            if (!name)
                return false;
            id = self.item.data('item-id');
            var contentHolder = $('#structure-tab .tpp-dt-content');
            contentHolder.html(self.loader);
            self.hideOverlay();

            $.post(self.structureURL, {
                    name: name, 
                    id: id, 
                    action: action, type: 'vacancy', 
                }, function(data) {
                    contentHolder.replaceWith(data);
            } , 'html');


            return false;
        });

        // press Cancel button
        form.on('click','.btntype1', function() {
            self.hideOverlay();
            return false;
        });

        this.showOverlayForm(form);
    },

    showOverlayForm: function(form) {

        this.hideOverlay();

        this.overlay.show();

        this.form = form;

        $('body').append(this.form);
    },

    hideOverlay: function() {

        if (this.form) {
            this.form.remove();
            delete this.form;
        }

        this.overlay.hide();
    }
};

var companyStaff =
{
    overlay: '#fade-profile',

    forms: '',

    staffURL: "",
    cache: {},

    loader: '<div class="loader">' +
                '<img class="loader-img" src="' + statciPath + 'img/ajax-loader.gif"/>' +
            '</div>',

    init: function(staffURL, LANG) {

        this.LANG = LANG;

        var self = this;

        self.staffURL = staffURL;
        self.overlay = $(this.overlay);

        self.setForms();

        $('#user-add-button').on('click', function() {
            return self.addNew($(this));
		});

        $('.btnremove-small').on('click', function() {
            return self.removeStaff($(this));
		});
    },


    setForms: function() {

        var LANG = this.LANG;
        var staff_options = '';
        if (typeof STAFFGROUPS !== "undefined") {
            $.each(STAFFGROUPS, function(index, item) {
                staff_options += '<option value="' + item.value + '">' + item.name + '</option>';
            });
        }
        var extragroup_options = '';
        if (typeof EXTRAGROUPS !== "undefined") {
            $.each(EXTRAGROUPS, function(index, item) {
                extragroup_options += '<span style="float: left; margin-right: 10px;">' +
                    '<input type="checkbox" id="id-extragroup-' + item.value + '">' + item.name +
                '</span>';
            });
        }

        this.form =
                        '<div class="staffadd" id="add-user-popup">' +
                            '<i class="close-formadd imgnews"></i>' +
                            '<div class="title">' + LANG['popup_title'] + '</div>' +
                            '<div class="error"></div>' +
                            '<div id="popup-context">' +
                                '<div class="staffaddin">' +
                                    '<div class="holder">' +
                                        '<label>' + LANG['popup_dep'] + '</label>' +
                                        '<select id="dep-list" style="width:62%;">' +
                                           '<option disabled selected>' + LANG['popup_loading'] + '</option>' +
                                        '</select>' +
                                    '</div>' +
                                    '<div class="holder">' +
                                        '<label>' + LANG['popup_vac'] + '</label>' +
                                        '<select id="vacancy-list" style="width:62%;">' +
                                            '<option disabled selected>' + LANG['select_vacancy'] + '</option>' +
                                        '</select>' +
                                    '</div>' +
                                    '<div class="holder">' +
                                        '<input type="checkbox" id="is-admin">' + LANG['popup_administrator'] +
                                    '</div>' +
                                    '<div class="holder">' +
                                        '<input type="checkbox" id="is-hidden-user">' + LANG['popup_hidden_user'] +
                                    '</div>' +
                                    '<div class="title">' + LANG['popup_user_title'] + '</div>' +
                                    '<div class="inputadd">' +
                                            '<input type="text" id="user-name" class="text" />' +
                                    '</div>' + 
                                    '<div class="title">' + LANG['extra_permissions_title'] + '</div>' +
                                    '<div class="holder">' +
                                        '<input type="checkbox" id="for-children">' + LANG['popup_for_children'] +
                                    '</div>' +
                                    '<div class="holder">' +
                                        '<label>' + LANG['popup_staffgroup'] + '</label>' +
                                            '<select id="staffgroups" style="width: 100%">' +
                                                staff_options +
                                            '</select>' +
                                        '</lable>' +
                                    '</div>' +
                                    extragroup_options +
                                    '<div class="formadd-button">' +
                                        '<a class="btntype2" id="btn-add-user" href="#">' + LANG['popup_add'] + '</a>' +
                                        '<a class="btntype1" href="#">' + LANG['popup_cancel'] + '</a>' +
                                    '</div>' +
                                '</div>' +
                            '</div>' +
                        '</div>';
    },

    removeStaff: function(clickedItem) {
        var contentHolder = $('#staff-tabs');
        var id = clickedItem.closest('tr').find('i.staff-contact-msg').data('id');
        if(id && confirm(this.LANG['confirm'])) {
            contentHolder.html(this.loader);

            $.post(this.staffURL, {id: id, "action": "remove"}, function(data){
                contentHolder.replaceWith(data);
            }, 'html');
        }

        return false;
    },

    setOptions: function(select, options) {
        select.find('option').remove();
        for (i in options) {
            obj = options[i];
            select.append('<option value="' + obj.value + '">' + obj.name + '</option>');
        }
    },

    addNew: function(clickedItem) {

        var self = this;
        var form = $(self.form);

        form.on("change", "#dep-list", function() {
           var id = $(this).find("option:selected").val();
           var select = $('#vacancy-list');
           var option_loading = {'value': '', 'name': self.LANG['popup_loading']};
           var option_department = {'value': '', 'name': self.LANG['select_department']};

           if ( !id ) {
               self.setOptions(select, [option_department])
           } else {

               if ( id in self.cache )
               {
                   var options = self.cache[id];
                   self.setOptions(select, options);
               } else {
                   self.setOptions(select, [option_loading]);
                   $.get(self.staffURL, {"action": "vacancy", "department": id}, function(options) {
                       self.cache[id] = options;
                       self.setOptions(select, options);
                   }, 'json');
                   
               }
           }
        });

        // press Add button
	    form.on('click','#btn-add-user', function() {

            if (self.xhr)
                return false;

            var user = form.find('#user-name').val();
            var vacancy = form.find('#vacancy-list option:selected').val();
            var department = form.find('#dep-list option:selected').val();
            var admin = 0;

            if(!user || !vacancy || !department)
                return false;

            if (form.find('#is-admin').is(':checked'))
               admin = 1;

            var contentHolder = $('#staff-tabs');
            var error = form.find('.error');

            error.text(self.LANG['popup_loading']);

            self.xhr = $.ajax({
                url: self.staffURL,
                type: 'POST',
                data : {
                    action: "add",
                    user: user,
                    vacancy: vacancy,
                    admin: admin,
                    department: department
                },
                success: function (data) {
                    contentHolder.replaceWith(data);
                    self.hideOverlay();
                },
                error: function (xhr, status, error) {
                    if (error) {
                        console.log(xhr.responseText);
                        form.find('.error').text(xhr.responseText );
                    }
                },
                complete: function() {
                    delete self.xhr;
                },
                dataType: 'html'
            });

            return false;
		});

        <!-- press Cancel button -->
	    form.on('click','.btntype1', function() {
            self.hideOverlay();
            return false;
		});

        this.showOverlayForm(form);
    },

    showOverlayForm: function(form) {

        var self = this;

        self.hideOverlay();

        self.overlay.show();
        self.popup = form;

        var select = form.find('#dep-list');

        $.get(self.staffURL, {"action": "department"}, function(options) {
            self.setOptions(select, options);
        }, 'json');

        $('body').append(self.popup);
    },

    hideOverlay: function(form) {

        if (this.popup) {
            this.popup.remove();
            delete this.popup;
            this.cache = {};
        }

        this.overlay.hide();
    }
};

var chatsUI = {

    curChat: 'mess-cur' ,
    chatList: '.message-tabcontent',
    messageBox: '.message-box',
    textArea: '#message-box',
    submitSend: '#submit-send-message',
    messageForm: '#send-message-to-chat',
    
    getMessages: function(container) {
        if (container.hasClass(chatsUI.curChat))
            return false;
        var old = $(chatsUI.chatList + ' .' + chatsUI.curChat);
        if (old.length > 0) {
            old.removeClass(chatsUI.curChat);
        }
        container.addClass(chatsUI.curChat);
        var item_a = $(container).children('a:first');
        var chat_id = item_a.data('chat-id');
        $('#chat-id').val(chat_id);
        var url = item_a.data('url');
        $.get(url, function(data) {
            $('.custom-contentin').html(data);
        });
    },

    renewMessages: function() {
        var container = $(chatsUI.chatList + ' .' + chatsUI.curChat);
        if (container.length > 0) {
            var item_a = $(container).children('a:first');
            var url = item_a.data('url');
            $.get(url, function(data) {
                $('.custom-contentin').html(data);
            });
        }
    },

    onSelectChat: function() {
        var container = $(this);
        chatsUI.getMessages(container);
        return false;
    },

    sendMessage: function() {
        $(chatsUI.messageForm).ajaxSubmit({
            url: '/messages/chats/add/',
            type: 'post',
            success: function(data) {
                $("#send-message-to-chat")[0].reset();
                $(".file-message-attachment").not(":first").remove();
                chatsUI.renewMessages();
            }
        });
        return false;
    },

    init: function() {
        $(".messages-l").tabs({
            activate: function(event, ui) {
                var url = ui.newTab.find('a').data('url');
                var currentItem = $(ui.newPanel).find('.data-item:first');
                if (currentItem.length > 0) {
                    chatsUI.getMessages(currentItem);
                }
            },
        });
        this.messagesLoader = $('.message-loader');
        $(this.chatList).on('click', 'li.data-item', this.onSelectChat);
        $(this.submitSend).on('click', this.sendMessage);
        var current = $('.data-item:first');
        if (current.length > 0) {
            this.getMessages(current);
        }
        
    },

};
