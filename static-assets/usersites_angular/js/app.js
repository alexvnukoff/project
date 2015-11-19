var myApp = angular.module("myApp", ["ngRoute", "ngAnimate", 'angularUtils.directives.dirPagination',  'uiAccordion', 'gettext']);

myApp.run(function (gettextCatalog) {
    gettextCatalog.setCurrentLanguage();
});

myApp.constant('startPoint', '/api/');

myApp.config(['$routeProvider', '$locationProvider', function($routeProvider, $locationProvider) {


	$routeProvider
		.when("/home", {
			templateUrl: "partials/home.html",
			title: "Main Page",
			controller: "homeCtrl"
		})
		.when("/article/:slug", {
			templateUrl: "partials/article.html",
			controller: "articleCtrl"
		})
		.when("/contact", {
			templateUrl: "partials/contact.html",
			title: "Contact us now"
		})
		.when("/gallery", {
			templateUrl: "partials/gallery.html",
			title: "Gallery",
			controller: "galleryCtrl"
		})
		.when("/offers", {
			templateUrl: "partials/offers.html",
			title: "Offers",
			controller: "offersCtrl"
		})
        .when("/offers/:id", {
            templateUrl: "partials/one-offer.html",
            title: "Offer",
            controller: "oneOfferCtrl"
        })
		.when("/news", {
			templateUrl: "partials/news.html",
			title: "News",
			controller: "newsCtrl"
		})
        .when("/news/:id", {
            templateUrl: "partials/one-news.html",
            title: "News",
            controller: "oneNewsCtrl"
        })
		.when("/products/:sub", {
			templateUrl: "partials/products.html",
			title: "Our products",
			controller: "productsCtrl"
		})
        .when("/products/:sub/:id", {
            templateUrl: "partials/one-product.html",
            title: "Product",
            controller: "oneProductCtrl"
        })
		.when("/structure", {
			templateUrl: "partials/structure.html",
			title: "Company structure",
			controller: "structureCtrl"
		})
	.otherwise({
		redirectTo: "/home"
	});
}]);


myApp.factory('Page', function() {
   var title = 'default';
   return {
     title: function() { return title; },
     setTitle: function(newTitle) { title = newTitle }
   };
});


myApp.directive('fancybox', function() {
  return {
    restrict: 'A',
    link: function(scope, element) {
      if (scope.$last) setTimeout(function() {
       $('.fancybox').fancybox({
          theme : 'dark'
        });
       }, 1);
    }
  };
});

myApp.directive('timer', function() {
   var date = $('.timer').attr('date');
   return function(scope, element, attrs) {
       element.countdown({
            until: new Date(date),
            format: 'dHM'
       });
   }
});

myApp.directive('compact', function() {
   return function(scope, element, attrs) {
   		angular.forEach(element, function(){
   			element.countdown({
	            until: new Date(attrs.date),
	            compact: true
	       });
   		})
   }
});


myApp.directive('toggleClass', function() {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            element.bind('click', function() {
                element.toggleClass(attrs.toggleClass);
            });
        }
    };
});


myApp.directive('siteHeader', function () {
    return {
        restrict: 'E',
        scope: {
            back: '@back',
            icons: '@icons'
        },
        link: function(scope, element, attrs) {
            $(element[0]).on('click', function() {
                history.back();
                scope.$apply();
            });
        }
    };
});

myApp.directive('slick', function($timeout) {
    return function(scope, el, attrs) {
        $timeout((function() {
            el.slick({
                arrows: true,
                dots: true,
                infinite: true,
                autoplay: true,
                autoplaySpeed: 6500,
                speed: 1500,
                slidesToShow: 1,
                slidesToScroll: 1,
                fade: true,
                cssEase: 'linear'
            })
        }), 100)
    }
});

myApp.directive('formattedText', function() {
    return {
        restrict: 'A',
        scope: {},
        link: function($scope, $elem, $attrs) {
            var formattedText = $attrs['formattedText'];
            $elem.html(formattedText);
        }
    }
});

myApp.directive('preventDefaultBehavior', function(locationProvider) {
    return {
        restrict: 'A',
        scope: {},
        link: function($scope, $elem) {
            var before =

            $elem.on('click', function($event) {
                $event.preventDefault();
            });
        }
    }
});

myApp.filter('removeTags', function() {
    return function(input) {
        return angular.element(input).text();
    }
});

myApp.filter('currentLanguage', function($window) {
    return function() {
        var languages = {
            'en': 'English',
            'he': 'עברית',
            'ru': 'Русский',
            'ar': 'العربية',
            'hy': 'Armenian',
            'zh': '中国'
        };

        var lang = $window.location.hostname.substring(0, $window.location.hostname.indexOf('.'));

        return languages[lang] || 'English';
    }
});

myApp.controller('title', function($scope, $http, gettextCatalog, Page) {
	$scope.Page = Page;
});

myApp.controller('title', function($scope, $http, gettextCatalog, Page) {
	$scope.Page = Page;
});

myApp.controller('mainInfoCtrl', function($scope, $http, $window, gettextCatalog, startPoint) {

	$scope.toggleCateg = function() {
        $scope.show = !$scope.show;
    }

  	$scope.hideCateg = function() {
        $scope.show = false;
    }

    // Implemented
    $http.get(startPoint).success(function(response) {
        $scope.siteBar = response;
    });

    // Implemented
    $http.get(startPoint + 'settings/').success(function(response) {
        $scope.settings = response;

        $scope.settings.contacts.phone = angular.element($scope.settings.contacts.tel).text();
        $scope.settings.contacts.tel = $scope.settings.contacts.phone.replace('-', '');
    });

    // Choose default language by current url
    function chooseDefaultLanguage(lang, needNavigate) {
        var hostname = $window.location.host;
        var subWithoutPrefix = $window.location.host.substring($window.location.host.indexOf('.') + 1);
        var subdomain = lang.indexOf('_') > -1 ? lang.substring(0, lang.indexOf('_')) : lang;

        //$window.location.href = 'http://' + subdomain + '.' + subWithoutPrefix + '/' + $window.location.hash;

        var languages = ['en', 'he', 'ru', 'ar', 'hy', 'zh'];
        var codes = ['en', 'he_IL', 'ru', 'ar', 'hy_AM', 'zh'];
        var titles = [];

        //var sub = hostname.indexOf('.') > -1 ? hostname.substring(0, hostname.indexOf('.')) : 'en';

        if (languages.indexOf(subdomain) > -1) {
            var pos = languages.indexOf(subdomain);
            gettextCatalog.setCurrentLanguage(codes[pos]);
        } else {
            gettextCatalog.setCurrentLanguage('en');
            subdomain = 'en';
        }

        if (needNavigate) {
            $window.location.href = 'http://' + subdomain + '.' + subWithoutPrefix + '/' + $window.location.hash;
        }
    }

	$scope.changeLang = function (lang) {
        gettextCatalog.setCurrentLanguage(lang);
        // console.log(lang);

        chooseDefaultLanguage(lang, true);
    }
    $scope.language = 'English';

    var prefix = $window.location.host.substring(0, $window.location.host.indexOf('.'));
    chooseDefaultLanguage(prefix, false);
});

myApp.controller("contentCtrl", function($scope, $http){

	$scope.class = "grid-layout";

	$scope.gridClass = function(){
          if ($scope.class === "layout"){
            $scope.class = "grid-layout";
        };
	};

	$scope.layoutClass = function(){
          if ($scope.class === "grid-layout"){
            $scope.class = "layout";
        };
	};

});


myApp.controller("homeCtrl", function($scope, $http, Page, startPoint){

	Page.setTitle('Главная страница');

    // TODO: Implemented
    // $http.get(startPoint + 'categories/').success(function(response) {
    //     $scope.categories = response;
    // });

    // Implemented
    $http.get(startPoint + 'coupons/').success(function(response) {
        $scope.coupons = response;
    });

    // Implemented
    $http.get(startPoint + 'news/').success(function(response) {
        $scope.news = response;
    });

    // Implemented
	$http.get(startPoint + 'products/b2b/').success(function(response) {
		$scope.products = response;
	});

});

myApp.controller("galleryCtrl", function($scope, $http, Page, startPoint) {
    // Implemented
    $http.get(startPoint + 'gallery/').success(function(response) {
        $scope.galleryImages = response;
    });

	Page.setTitle('Галлерея');
});




myApp.controller("offersCtrl", function($scope, $http, Page, startPoint){
	Page.setTitle('Бизнес предложения');

    // Implemented
    $http.get(startPoint + 'offers/').success(function(response) {
        $scope.offers = response;
    });
});



myApp.controller("newsCtrl", function($scope, $http, Page, startPoint){
	Page.setTitle('Новости компании');

    // Implemented
    $http.get(startPoint + 'news/').success(function(response) {
        $scope.news = response;
    });
});



myApp.controller("productsCtrl", function($scope, $http, Page, startPoint, $routeParams, $window){
	Page.setTitle('Наши продукты');
    var url = startPoint + 'products/' + $routeParams.sub;

    $http.get(url).success(function(response) {
        $scope.products = response;
    });

    function getCategories(categoriesData) {
        var categories = {};
        var allData = angular.copy(categoriesData);

        for (var i = 0; i < allData.length; i++) {
            var c = allData[i];

            if (categories['' + c.parentId] === undefined) {
                categories['' + c.parentId] = [];
                categories['' + c.parentId].push(c);
            } else {
                categories['' + c.parentId].push(c);
            }
        }

        function getParentIdById(id) {
            for (var i = 0; i < allData.length; i++) {
                if (allData[i].id == id) {
                    return allData[i].parentId;
                }
            }
        }

        for (property in categories) {
            if (categories.hasOwnProperty(property) && property != 'null') {
                var parentId = getParentIdById(property);

                for (var j = 0; j < categories['' + parentId].length; j++) {
                    var el = categories['' + parentId][j];

                    if (el.id == property) {
                        if (el.subCategories === undefined) {
                            el.subCategories = [];
                        }

                        for (var k = 0; k < categories[property].length; k++) {
                            el.subCategories.push(categories[property][k]);
                        }
                    }
                }
            }
        }

        return categories['null'];
    }

    $http.get(url + '/categories/').success(function(response) {
        $scope.categories = getCategories(response);
    });

    $scope.getCurrentUrl = function() {
        return $window.location.href;
    }
});



myApp.controller("structureCtrl", function($scope, $http, Page, startPoint){
	Page.setTitle('Структура компании');

    // Implemented
    $http.get(startPoint + 'structure/').success(function(response) {
        $scope.structure = response;
    });
});



myApp.controller("articleCtrl", function($scope, $http, $location, Page){

	var file = $location.path().split("/")[2];

	$http.get("posts/" + file + ".json")
		.success(function(response) {
			$scope.article = response;
			Page.setTitle($scope.article.title);
		})
		.error(function(){
			$location.path('#/home');
		})

});

myApp.controller('oneNewsCtrl', function($scope, $http, $routeParams, Page, startPoint) {
    $http.get(startPoint + 'news/' + $routeParams.id).success(function(response) {
        $scope.news = response;

        var title = angular.element($scope.news.title).text();
        Page.setTitle(title);
    });
});

myApp.controller('oneOfferCtrl', function($scope, $http, $routeParams, Page, startPoint) {
    $http.get(startPoint + 'offers/' + $routeParams.id).success(function(response) {
        $scope.offer = response;

        var title = angular.element($scope.offer.title).text();
        Page.setTitle(title);
    });
});

myApp.controller('oneProductCtrl', function($scope, $http, $routeParams, Page, startPoint) {
    $http.get(startPoint + 'products/' + $routeParams.sub + '/' + $routeParams.id).success(function(response) {
        $scope.product = response;

        var title = angular.element($scope.product.name).text();
        Page.setTitle(title);
    });
});
