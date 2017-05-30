donationRoad.directive('followLink', function() {
	return {
		restrict : 'C',
		link : function(scope, element, attr) {
			element.on('mouseover', function() {
				if ($(this).text() == 'Following') {
					$(this).removeClass('following').addClass('unfollow').text('Unfollow');
				}
			});

			element.on('mouseleave', function() {
				if ($(this).text() == 'Unfollow') {
					$(this).removeClass('unfollow').addClass('following').text('Following');
				}

			});

		}
	};
})
.directive('followLink', function(Relationship, CampaignService) {
    return {
        restrict : 'E',
        replace: true,
        template:'<a href="#" class="follow-link">Follow</a>',
        scope: {objectId:'@', objectType:'@', followed:'=', objectVar:'@'},
        link : function(scope, element, attr) {
            scope.$watch('followed', function(value){
            if (value) {
                element.addClass('following');
                element.removeClass('follow');
                element.text('Following');
                scope.action='unfollow';
                }
            else {
                element.addClass('follow');
                element.removeClass('following');
                element.text('Follow');
                scope.action='follow';
            }
            });

            scope.$on("action_success", function(event, data){

            });

            element.on('click', function() {
                var result = Relationship.set_relation(scope.action,
                                          {object_id:scope.objectId,
                                           object_type:scope.objectType});
                result.success(function(response){
                if (response.success && (scope.objectType != 'campaign' || (scope.objectType == 'campaign'&&typeof(CampaignService['campaign' + scope.objectId]) == 'undefined'))) {
                    scope.followed = response.data.action=='follow';

                    if (scope.objectType == 'campaign' && typeof(CampaignService['campaign' + scope.objectId]) == 'undefined' && scope.objectVar) {
                        scope.$parent[scope.objectVar].numberOfDRFollowers = response.data.total;
                    }
                }
                else if (response.success && scope.objectType == 'campaign') {
                    CampaignService['campaign' + scope.objectId].is_followed = response.data.action=='follow';
                    CampaignService['campaign' + scope.objectId].numberOfDRFollowers = response.data.total;
                }
                                           });
               scope.$emit('action_success', result.$$v);

            });

        }
    };
});
