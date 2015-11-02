var myApp = angular.module("myApp", ["ngRoute", "ngAnimate", 'angularUtils.directives.dirPagination',  'uiAccordion']);

myApp.config(function($routeProvider) {
	$routeProvider
		.when("/home", {
			templateUrl: "partials/home.html",
			title: "Main Page"
		})
		.when("/contact", {
			templateUrl: "partials/contact.html",
			title: "Contact us now"
		})
		.when("/gallery", {
			templateUrl: "partials/gallery.html",
			title: "Gallery"
		})
		.when("/offers", {
			templateUrl: "partials/offers.html",
			title: "Offers"
		})
		.when("/news", {
			templateUrl: "partials/news.html",
			title: "News"
		})
		.when("/products", {
			templateUrl: "partials/products.html",
			title: "Our products"
		})
		.when("/structure", {
			templateUrl: "partials/structure.html",
			title: "Company structure"
		})
	.otherwise({
		redirectTo: "/home"
	});
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
})

myApp.controller('mainInfoCtrl', function($scope, $http) {


	$scope.toggleCateg = function(){
    		$scope.show = !$scope.show
  		}
  		$scope.hideCateg = function(){
    		$scope.show = false
  		}

	$http.get("pharm-sp/siteBarMenu.json")
		.success(function(response) {$scope.siteBar = response;});

	$http.get("pharm-sp/settings.json")
		.success(function(response) {$scope.settings = response;});


    $scope.menu = [
	        "קוסמטיקה רפואית",
	        "מכון אורטופדי",
	        "מוצרי קוסמטיקה",
	        "אודות",
	        "בית מרקחת"
    ];


    $scope.contacts = {
    		phone: "054-6449654",
            tel: "0546449654",
            email: "email@email.com",
            address: "84201 רח' קקל 94 באר שבע 84201",
            orgName: "Member of Торгово-промышленная палата и промышленности Баэр-Шева и Негев, Израиль"
    };
    
    $scope.logo =   'images/logo.png';
    $scope.offerIcons = [
	        {
				url: 'images/icon-1.jpg'
			},
			{
				url: 'images/icon-2.jpg'
			},
			{
				url: 'images/icon-3.jpg'
			},
			{
				url: 'images/icon-4.jpg'
			},
			{
				url: 'images/icon-5.jpg'
			}
    ];


    $scope.orgLogo      =   "images/organization-logo.jpg";
    $scope.footerBanner =   "images/banner.jpg";
});

myApp.controller("contentCtrl", function($scope, $http){

		$http.get("pharm-sp/categories.json")
			.success(function(response) {$scope.categories = response.categories;});

		$http.get("pharm-sp/structure.json")
			.success(function(response) {$scope.structure = response.structure;});


  		$http.get("pharm-sp/actions.json")
			.success(function(response) {$scope.actions = response.actions;});


		$http.get("pharm-sp/article.json")
			.success(function(response) {
				$scope.article = response;
			});

		$http.get("pharm-sp/news.json")
			.success(function(response) {$scope.news = response.news;});


		$http.get("pharm-sp/products.json")
			.success(function(response) {
					$scope.allProducts = response.products;
					$scope.products = $scope.allProducts.all;
				});

		$scope.selectCategory = function(value){
			$scope.show = false;
			switch (value) {
					case "econom":
						$scope.products = $scope.allProducts.econom;
						break
					case "business":
						$scope.products = $scope.allProducts.business;
						break
					case "luxury":
						$scope.products = $scope.allProducts.luxury;
						break
				}
		};



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

	$http.get("pharm-sp/offers.json")
		.success(function(response) {$scope.offers = response.offers;});



	$http.get("pharm-sp/gallery.json")
		.success(function(response) {$scope.galleryImages = response.gallery;});


});


