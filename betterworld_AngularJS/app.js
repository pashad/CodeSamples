
// currently we have only one and it is global. But we 'll add more later to specialize our modules
var donationRoad = angular.module('donationRoad', [ 'ng', 'ngRoute', 'ngAnimate', 'ngSanitize', 'masonry', 'angular-svg-round-progress',
    'google-maps', 'ngDropdowns', 'ngDialog', 'ngCookies', 'filters', 'djangoUrls', 'ngResource','LocalStorageModule',
    'wysiwyg.module', 'colorpicker.module', 'dibari.angular-ellipsis', 'ngFacebook']);

'use strict';

donationRoad.config(function($interpolateProvider, $facebookProvider) {
    $interpolateProvider.startSymbol('{$');
    $interpolateProvider.endSymbol('$}');
    $facebookProvider.setAppId(initial_data.data.facebook_app_id)
});

/*
 * Declare all routes here
 */

donationRoad.config(['$routeProvider','$locationProvider', function ($routeProvider,$locationProvider) {
    // routes will go here

}]);

donationRoad.config(['$resourceProvider', function ($resourceProvider) {
       // Don't strip trailing slashes from calculated URLs
       //$resourceProvider.defaults.stripTrailingSlashes = false;
     }]);

angular.module('filters',[])
    .filter('daysLeft', function() {
        return function(input) {
            if ( !input )
                return;
            var today = new Date();
            var endDate = new Date(input.split('-').reverse().join('-'));
            var diff = Math.floor(endDate.getTime() - today.getTime());
            var day = 1000* 60 * 60 * 24;

            return Math.floor(diff/day);

        };
    })
    .filter('urlencode', function(){
        return function(value){
            if ( !value )
                return;
            return encodeURIComponent(value);
        };
    });