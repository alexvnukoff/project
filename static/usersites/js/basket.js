
var app = angular.module("myApp", []);
    app.config(function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });


app.controller('MyAwesomeBasket', ['$scope', '$http', function($scope, $http) {

    var source_url = '/b2c-products/basket.html';

    $http.get(source_url + '?count=1').error(function(data, status) {
        console.log(data, status);
    }).success(function(data, status) {
        $scope.basket_count = data['basket_count'];
    });

    $scope.addToBasket = function(d) { req(d); $scope.add_to_basket = true; }
    $scope.deleteBasket = function(d) {
    $http.get(source_url + '?delete=1').error(function(data, status) {
        console.log(data, status);
    }).success(function(data, status) {
        window.location = source_url;
    });
    }

    var req = function(d) {

        $http({
          method : 'POST',
          url    : source_url,
          data   : { 'product_id': d}
         }).error(function(data, status) {
            console.log(data, status);
        }).success(function(data, status) {
            $scope.basket_count = data['basket_count'];
            });
        }

}]);



