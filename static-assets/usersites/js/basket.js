/*
 AngularJS v1.4.7
 (c) 2010-2015 Google, Inc. http://angularjs.org
 License: MIT
*/
(function(p,c,n){'use strict';function l(b,a,g){var d=g.baseHref(),k=b[0];return function(b,e,f){var g,h;f=f||{};h=f.expires;g=c.isDefined(f.path)?f.path:d;c.isUndefined(e)&&(h="Thu, 01 Jan 1970 00:00:00 GMT",e="");c.isString(h)&&(h=new Date(h));e=encodeURIComponent(b)+"="+encodeURIComponent(e);e=e+(g?";path="+g:"")+(f.domain?";domain="+f.domain:"");e+=h?";expires="+h.toUTCString():"";e+=f.secure?";secure":"";f=e.length+1;4096<f&&a.warn("Cookie '"+b+"' possibly not set or overflowed because it was too large ("+
f+" > 4096 bytes)!");k.cookie=e}}c.module("ngCookies",["ng"]).provider("$cookies",[function(){var b=this.defaults={};this.$get=["$$cookieReader","$$cookieWriter",function(a,g){return{get:function(d){return a()[d]},getObject:function(d){return(d=this.get(d))?c.fromJson(d):d},getAll:function(){return a()},put:function(d,a,m){g(d,a,m?c.extend({},b,m):b)},putObject:function(d,b,a){this.put(d,c.toJson(b),a)},remove:function(a,k){g(a,n,k?c.extend({},b,k):b)}}}]}]);c.module("ngCookies").factory("$cookieStore",
["$cookies",function(b){return{get:function(a){return b.getObject(a)},put:function(a,c){b.putObject(a,c)},remove:function(a){b.remove(a)}}}]);l.$inject=["$document","$log","$browser"];c.module("ngCookies").provider("$$cookieWriter",function(){this.$get=l})})(window,window.angular);
//# sourceMappingURL=angular-cookies.min.js.map

var app = angular.module("myApp", ['ngCookies']);
    app.config(function($httpProvider) {
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    });

app.controller('MyAwesomeBasket', ['$scope', '$http', '$cookies', '$timeout', function($scope, $http, $cookies, $timeout) {
    $scope.getMyCount = function() {
        $scope.basket_count = $cookies.get('b24online_bscookie_q_true');
    }

    $http.get('/b2c-products/basket.html?get_stat=1').then(function success(response) {
        $cookies.put('b24online_bscookie_q_true', response['data'].quantity__sum);
        $scope.getMyCount();
    }, function error(response) {
        $cookies.put('b24online_bscookie_q_true', 0);
        $scope.getMyCount();
    });

    $scope.addToBasket = function(pk,quantity) {
        if(!quantity) { quantity = 1; }
        $http.get('/b2c-products/basket.html?pk=' + pk + '&q=' + quantity).then(function success(response) {
            $cookies.put('b24online_bscookie_q_true', response['data'].quantity__sum);
            $scope.getMyCount();
            $scope.add_to_basket = true;
        }, function error(response) {
            console.log(response['status']);
        });

        $timeout(function() {
            $scope.add_to_basket = false;
        }, 800);

    }
}]);



