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

myApp.controller('title', function($scope, $http, gettextCatalog, Page) {
	$scope.Page = Page;
});

myApp.controller('title', function($scope, $http, gettextCatalog, Page) {
	$scope.Page = Page;
});

myApp.controller('mainInfoCtrl', function($scope, $http, gettextCatalog, startPoint) {

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
    $http.get(startPoint + '/settings').success(function(response) {
        $scope.settings = response;

        $scope.settings.contacts.phone = angular.element($scope.settings.contacts.tel).text();
        $scope.settings.contacts.tel = $scope.settings.contacts.phone.replace('-', '');
    });

	$scope.changeLang = function (lang) {
        gettextCatalog.setCurrentLanguage(lang);
        console.log(lang);
    }

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
    $http.get(startPoint + 'categories/').success(function(response) {
        $scope.categories = response;
    });

    // Implemented
    $http.get(startPoint + '/coupons').success(function(response) {
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



myApp.controller("productsCtrl", function($scope, $http, Page, startPoint, $routeParams){
	Page.setTitle('Наши продукты');

    $http.get(startPoint + 'products/' + $routeParams.sub).success(function(response) {
        $scope.products = response;
    });

    // TODO: must be Implemented!!!
	$http.get("categories.json")
		.success(function(response) {$scope.categories = response.categories;});

	$scope.selectCategory = function(value){
		console.log(value);
		$http.get("products.json?category=" + value)
			.success(function(response) {
				$scope.products = response.products;
			});
	};

});



myApp.controller("structureCtrl", function($scope, $http, Page, startPoint){
	Page.setTitle('Структура компании');

    // Implemented
    $http.get(startPoint + '/structure').success(function(response) {
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
    $http.get(startPoint + '/news/' + $routeParams.id).success(function(response) {
        $scope.news = response;

        var title = angular.element($scope.news.title).text();
        Page.setTitle(title);
    });
});

myApp.controller('oneOfferCtrl', function($scope, $http, $routeParams, Page, startPoint) {
    $http.get(startPoint + '/offers/' + $routeParams.id).success(function(response) {
        $scope.offer = response;

        var title = angular.element($scope.offer.title).text();
        Page.setTitle(title);
    });
});
