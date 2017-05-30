/*
 * It is parent controller. All child controller can access it attributes via $rootScope
 * All common function should be placed in this controller
 */
donationRoad.controller('mainCtrl', ['localStorageService', '$scope', '$sce', '$timeout', '$interval',
    '$rootScope', '$route', '$location', '$resource', '$http',
    'EntityService', 'BaseService', 'djUrlsService', 'CampaignService',
    'ngDialog', 'validateUrl', '$window',
    function(localStorageService, $scope, $sce, $timeout, $interval, $rootScope, $route, $location,
        $resource, $http, EntityService, BaseService, djUrlsService, CampaignService, ngDialog, validateUrl, $window) {

        $http.defaults.headers.post['X-CSRFToken'] = window.JS_CSRF_TOKEN;

        djUrlsService.get_urls.then(function(data) {
            $rootScope.urls_map = data.data;
        });

        $rootScope.header = true;

        $rootScope.toggleBackDisable = function() {
            $rootScope.disabledBackBtn = true;
            $timeout(function() {
                $rootScope.disabledBackBtn = false;
            }, 750);
        };

        $scope.login_redirect_next = {
            next: window.location.pathname
        };

        $scope.invite = {
            invite: 1
        };

        $scope.login_popup = function(sign_in) {
            $rootScope.login_popup_header = {};
            $rootScope.login_popup_header.text = (sign_in ? "in" : "up");
            console.log($rootScope.login_header_text);
            var d = ngDialog.open({
                template: '/static/js/apps/templates/popups/login.html',
                className: 'ngdialog-donationroad popup-wrapper popup-angular login-popup',
                scope: $scope
            });
        };

        $rootScope.go = function(pathName) {
            $rootScope.toggleBackDisable();
            if (typeof gaPlugin !== "undefined") {
                gaPlugin.trackPage(nativePluginResultHandler, nativePluginErrorHandler, "/" + pathName);
            }
            $navigate.go("/" + pathName);
        };

        $rootScope.noInternetTimerMsg = function() {
            if ($rootScope.internetMsgShown == false) {
                $rootScope.internetMsgShown = true;
                popupTimer.show({
                    modal_content: "There is no Internet Connectivity."
                }, null, 5000);
            }
        };

        $scope.$on('valuesUpdated', function() {
            localStorageService.set('activeCampaignHeader', BaseService.activeHeaderLabel);
            $scope.activeLink = localStorageService.get('activeCampaignHeader');
        });
        $scope.activeLink = localStorageService.get('activeCampaignHeader');

        $scope.invite_emails = [{
            email: "",
            validated: false,
            has_error: false
        }];

        $scope.add_invite_email = function() {
            if ($scope.invite_emails.length < 5) {
                $scope.invite_emails.push({
                    email: "",
                    validated: false,
                    has_error: false
                });
            } else {
                $scope.use_multi_invite = true;
            }
        };

        $scope.invites_count = 0;
        $scope.csv_uploader_error = false;


        $scope.add_user_search_email = function($event, email) {
            if ($scope.invite_emails.length < 5) {
                $scope.invite_emails[$scope.invite_emails.length - 1] = {
                    'has_error': false,
                    'validated': false,
                    'email': email
                };
                $scope.collect_email($event, email);
            }
        };

        $scope.check_user_search_email = function(email) {
            for (var i in $scope.invite_emails) {
                if ($scope.invite_emails[i].email == email) {
                    return true;
                }
            }
            return false;
        };

        $scope.collect_email = function($event, email, role) {
            if (typeof role == 'undefined') {
                role = 'supporter';
            }
            var get_email_index = function(email) {
                for (var i in $scope.invite_emails) {
                    if ($scope.invite_emails[i].email == email) {
                        return i;
                    }
                }
            };
            EntityService.collect_email(email, role).then(function(item) {
                var ind = get_email_index(email);

                if (item.success == true) {
                    $scope.add_invite_email();
                    $scope.invite_emails[ind].validated = true;
                    $scope.invite_emails[ind].has_error = false;
                    $scope.invites_count += 1;
                    if ($scope.invite_popup_haserrors != true && $scope.invite_popup_closequery == true)
                        ngDialog.close();
                    if ($scope.invite_force_send) {
                        $scope.send_collected_now();
                    } else {
                        $scope.save_angular_variables({
                            invite_emails: $scope.invite_emails,
                            invites_count: $scope.invites_count
                        }, false);
                    }
                } else {
                    $scope.invite_emails[ind].has_error = true;
                    $scope.invite_popup_haserrors = true;

                }

            });
        };

        $scope.invite_popup_closequery = false;
        $scope.invite_force_send = false;

        $scope.send_invitations = function() {
            var role = "supporter";
            if ($scope.send_invitations.arguments.length > 0) {
                if ($scope.send_invitations.arguments[0].force_send) $scope.invite_force_send = true;
                if ($scope.send_invitations.arguments[0].role) role = $scope.send_invitations.arguments[0].role;
            }
            $scope.invite_popup_haserrors = false;
            var ind = $scope.invite_emails.length - 1;
            var email = $scope.invite_emails[ind].email;
            var elem = $('div.email-invite-line .line input')[ind];
            $scope.invite_popup_closequery = true;
            if (email != '') {
                $scope.collect_email({
                    srcElement: elem
                }, email, role);
            } else {
                $scope.save_angular_variables({
                    invite_emails: $scope.invite_emails,
                    invites_count: $scope.invites_count
                }, false);

                $scope.invite_emails[ind].has_error = false;
                if ($scope.invite_force_send) {
                    $scope.send_collected_now();
                }
                ngDialog.close();

            }

        };

        $scope.send_collected_now = function() {
            BaseService.send_collected_invites($scope.object_id,
                $scope.object_type);
            $scope.save_angular_variables({
                invite_emails: [],
                invites_count: 0
            }, false);
            $scope.invite_emails = [{
                email: "",
                validated: false,
                has_error: false
            }];
            $scope.invites_count = 0;
        };

        $scope.save_angular_variables = function(values, persist) {
            var sval = JSON.stringify(values);
            BaseService.save_values(sval, persist);

        };

        $scope.get_notifications = function() {
            EntityService.get_notifications().then(function(item) {
                if (item.success) {
                    $scope.notifications = [];
                    $.each(item.messages, function(idx) {
                        var notify = {
                            id: item.messages[idx].id,
                            text: $sce.trustAsHtml(item.messages[idx].text)
                        };
                        $scope.notifications.unshift(notify);
                    });
                    $scope.unread_nots_count = item.total_unread;
                    $scope.nots_count = item.total;
                    $scope.notifications_popup = $scope.nots_count == 0;
                }

            });
        };
        $scope.notifications_limit = 5;
        //$scope.get_notifications();

        $scope.show_notify_all = function() {
            $scope.notifications_limit = $scope.nots_count;
        };

        $scope.get_unread_nots_count = function() {
            EntityService.get_unread_count().then(function(item) {
                if (item.success) {
                    $scope.unread_nots_count = item.total_unread;
                }
            });
        };

        $scope.delete_notify = function(_id) {
            EntityService.delete_notify(_id).then(function(item) {
                if (item.success) {
                    $scope.get_notifications();
                }
            });
        };

        $rootScope.play_campaign = function(event, vimeo) {
            $rootScope.play_url = validateUrl.getValidUrl(vimeo);
            $rootScope.video_loaded = true;
            var d = ngDialog.open({
                template: '/static/js/apps/templates/popups/play.html',
                className: 'ngdialog-donationroad popup-wrapper popup-angular play',
                scope: $rootScope
            });
        };

        $interval($scope, $scope.get_unread_nots_count(), 60000);

        $.extend(true, $scope, initial_data['data']);
        $.extend(true, $scope, initial_data['persist']);

        if ($scope.page_type == "campaign_page") $scope.invite_force_send = true;

        $scope.approve_charity = function(event, charity, action) {
            EntityService.approve_charity(charity.id, action).then(function(item) {
                if (item.data.success == true) {
                    $scope.messageBody = 'Charity was successfully ' + action + 'd';
                    $scope.messageTitle = 'Confirmation';
                } else {
                    $scope.messageBody = item.data.error;
                    $scope.messageTitle = 'Error';
                }
                charity.is_approved = action == 'approve';
                var d = ngDialog.open({
                    template: '/static/js/apps/templates/popups/message_final.html',
                    className: 'ngdialog-donationroad popup-wrapper popup-angular',
                    scope: $scope
                });

            });
        };

        $scope.$watch('popularMasonryVisible', function(value) {
            if (value) {
                $rootScope.$broadcast('masonry.reload');
            }
        });

        $scope.$watch(function() {
            return $window.innerWidth;
        }, function(value) {
            $scope.ww = value;
        });


        $scope.desktop_mode = function(action) {
            BaseService.desktop_mode(action).then(function(item) {
                if (item.success) {
                    $window.location.reload();
                }
            });
        };

    }
]);