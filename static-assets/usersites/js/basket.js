// using jQuery
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
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

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



