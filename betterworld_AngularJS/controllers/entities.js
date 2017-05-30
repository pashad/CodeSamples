donationRoad.controller('EntitiesCtrl', ['$scope', '$rootScope', '$compile', '$timeout',
    '$sce', 'validateUrl', 'EntityService', 'ngDialog',
    function($scope, $rootScope, $compile, $timeout, $sce, validateUrl, EntityService,
        ngDialog) {

        $timeout(function() {
            if ($scope.entity.type == 'charity' || $scope.entity.type == 'company') {
                $scope.entity.get_admins($scope.entity.slug);
                $scope.entity.get_members($scope.entity.slug);
                $scope.entity.get_supporters($scope.entity.slug);
                $scope.entity.get_partners($scope.entity.slug);
                if ($scope.entity.type == 'company') {
                    $scope.entity.get_supported_charities($scope.entity.slug);
                }
            }
            if ($scope.entity.type == 'account') {
                $scope.entity.get_charities($scope.entity.slug);
                $scope.entity.get_supported_charities($scope.entity.slug);
                $scope.entity.get_friends($scope.entity.slug);
                $scope.entity.get_companies($scope.entity.slug);
            }
            if (typeof($scope.entity.type) != 'undefined') {
                $scope.entity.get_following($scope.entity.slug);
                $scope.entity.get_followers($scope.entity.slug);
                $scope.entity.active_tab = $scope.entity.type == 'account' ? 'charities' : 'about';
            }
        });

        $scope.missions = true; // variable which show/hide missions(followers,ongoing projects) content
        $scope.show_back_arrow = false; //variable which show/hide left arrow

        $scope.entity = {
            tabs: {
                wall: false,
                map: true
            }
        };

        //Tabs
        $scope.entity.people = {
            active_tab: 'following'
        };
        $scope.entity.charities = {
            active_tab: 'owned'
        };

        $scope.currency_icons = {
            1: '$',
            2: '&pound;',
            3: '&yen;',
            4: '&euro;'
        };
        $scope.entity.avatar_handlers = {
            FileUploaded: function(uploader, file, response) {
                var result = jQuery.parseJSON(response.response);
                $scope.avatar_uploading = false;
                if (result['success']) {
                    var cFile = result['files'][0];

                    $scope.avatar_cropped = validateUrl.getValidUrl(cFile['url']);
                    $scope.avatar_initial_crop = null;
                    $scope.entity.avatar_id = cFile['id'];

                    $scope.$apply();
                }
            },
            UploadProgress: function(uploader, file) {
                $scope.avatar_uploading = true;
                $scope.avatar_upload_percent = uploader.total.percent;
                $scope.$apply();

            },
            FilesAdded: function(uploader, files) {
                $scope.avatar_cropped = '';
                $scope.$apply();
            }
        };

        $scope.entity.avatar_crop_selected = function(coords) {
            $scope.entity.avatar_crop = [Math.round(coords.x), Math.round(coords.y), Math.round(coords.x2), Math.round(coords.y2)].join(' ');

        };

        $scope.entity.like = function(entity_id) {
            var a = arguments;
            EntityService.like(entity_id).then(function(item) {
                if (item.success == true) {
                    if (a.length != 2) {
                        $scope.entity.liked = true;
                        $scope.entity.likes += 1;
                    } else {
                        a[1].is_liked = true;
                        a[1].numberOfDRLikes += 1;
                    }
                }
            });
        };

        $scope.entity.unlike = function(entity_id) {
            var a = arguments;
            EntityService.unlike(entity_id).then(function(item) {
                if (item.success == true) {
                    if (a.length != 2) {
                        $scope.entity.liked = false;
                        $scope.entity.likes -= 1;
                    } else {
                        a[1].is_liked = false;
                        a[1].numberOfDRLikes -= 1;
                    }
                }
            });
        };

        $scope.entity.follow = function(obj, entity_id) {
            EntityService.follow(entity_id).then(function(item) {
                if (item.success == true) {
                    obj.following = true;
                }
            });
        };

        $scope.entity.unfollow = function(obj, entity_id) {
            EntityService.unfollow(entity_id).then(function(item) {
                if (item.success == true) {
                    obj.following = false;
                }
            });
        };

        $scope.entity.change_mission = function(entity_id) {
            EntityService.change_mission(entity_id, $scope.entity.mission).then(function(item) {
                if (item.success == true) {
                    $scope.charity_mission = $scope.entity.mission;
                    $scope.charity_mission_html = $scope.charity_mission.replace(/\r\n/g, '<br />').replace(/[\r\n]/g, '<br />');
                    ngDialog.close();
                }
            });
        };

        $scope.entity.change_avatar = function(entity_id) {
            EntityService.change_avatar(entity_id, $scope.entity.avatar_id, $scope.entity.avatar_crop).then(function(item) {
                if (item.success == true) {
                    $scope.entity.avatar_thumb = item.thumbnail;
                    $scope.entity.avatar = item.avatar;
                    $scope.avatar_initial_crop = $scope.entity.avatar_crop;
                    ngDialog.close();
                }
            });
        };

        $scope.entity.toggle_fundraiser = function(fundraiser, type) {
            EntityService.toggle_fundraiser($scope.object_id, type).then(function(item) {
                if (item.success == true) {
                    $scope.entity.fundraising.types[type] = !$scope.entity.fundraising.types[type];
                    if (type == 'everyone' && $scope.entity.fundraising.types[type] == true) {
                        for (tp in $scope.entity.fundraising.types) {
                            $scope.entity.fundraising.types[tp] = true;
                        }
                    }
                    if (type != 'everyone' && $scope.entity.fundraising.types[type] == false) {
                        $scope.entity.fundraising.types['everyone'] = false;
                    }
                }
            });
        };

        $scope.entity.toggle_approve_fundraiser = function($event) {
            var el = angular.element($event.target);
            if (!el.hasClass('disabled')) {
                EntityService.toggle_approve_fundraiser($scope.object_id).then(function(item) {
                    if (item.success == true) {
                        $scope.entity.fundraising.approve_fundraisers = !$scope.entity.fundraising.approve_fundraisers;
                    }
                });
            }
        };

        $scope.get_str_amount = function(fundraiser) {
            var ret = '';
            var check = false;
            for (currency in fundraiser.total_amount) {
                if (fundraiser.total_amount[currency] > 0) {
                    ret += $scope.currency_icons[currency] + '' + fundraiser.total_amount[currency] + ' ';
                    check = true;
                }
            }
            if (!check) {
                ret = '0'
            }
            return ret
        };

        $scope.get_fundraiser_info = function(campaign_id) {
            var d = ngDialog.open({
                template: '/en/campaigns/' + campaign_id + '/fundraiser/',
                className: 'ngdialog-donationroad popup-wrapper popup-angular fundraiser-popup',
                scope: $scope,
                cache: false
            });
        };


        $scope.entity.edit_avatar = function() {
            $scope.avatar_cropped = $scope.entity.avatar;
            if ($scope.entity.avatar_crop != null)
                $scope.avatar_initial_crop = $scope.entity.avatar_crop.split(' ');

            var d = ngDialog.open({
                template: '/static/js/apps/templates/popups/avatar.html',
                className: 'ngdialog-donationroad popup-wrapper popup-angular',
                scope: $scope
            });
        };

        $scope.entity.get_friends = function(entity_id) {
            EntityService.get_friends(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.friends = item.friends;
                    $scope.entity.friends_total = item.total;

                }
            });
        };

        $scope.entity.get_following = function(entity_id) {
            EntityService.get_following(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.following = item.following;
                    $scope.entity.following_total = item.total;
                    $scope.entity.people_list = item.following;
                }
            });
        };

        $scope.entity.get_followers = function(entity_id) {
            EntityService.get_followers(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.followers = item.followers;
                    $scope.entity.followers_total = item.total;

                }
            });
        };

        $scope.entity.get_supporters = function(entity_id) {
            EntityService.get_supporters(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.supporters = item.objects;
                    $scope.entity.supporters_total = item.total;
                }
            });
        };

        $scope.entity.get_partners = function(entity_id) {
            EntityService.get_partners(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.partners = item.objects;
                    $scope.entity.partners_total = item.total;
                }
            });
        };

        $scope.entity.get_members = function(entity_id) {
            EntityService.get_members(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.members = item.objects;
                    $scope.entity.members_total = item.total;
                }
            });
        };

        $scope.entity.get_admins = function(entity_id) {
            EntityService.get_admins(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.admins = item.objects;
                    $scope.entity.admins_total = item.total;
                }
            });
        };

        $scope.entity.get_supported_charities = function(entity_id) {
            EntityService.get_supported_charities(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.supported_charities = item.objects;
                    $scope.entity.supported_charities_total = item.total;
                }
            });
        };

        $scope.entity.get_companies = function(entity_id) {
            EntityService.get_companies(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.companies = item.objects;
                    $scope.entity.companies_total = item.total;
                }
            });
        };

        $scope.entity.get_charities = function(entity_id) {
            EntityService.get_charities(entity_id).then(function(item) {
                if (item.success == true) {
                    $scope.entity.owned_charities = item.objects;
                    $scope.entity.owned_charities_total = item.total;
                    $scope.entity.charities_list = item.objects;
                }
            });
        };


        $scope.entity.set_default_bank = function(bankId) {
            EntityService.set_default_bank(bankId)
                .then(function(item) {
                    window.location.reload();
                });
        };


        $scope.entity.set_default_card = function(cardId) {
            EntityService.set_default_card(cardId)
                .then(function(item) {
                    window.location.reload();
                });
        };


        $scope.entity.changeMangopayBank = function(bankId) {
            for (var i = 0; i < $scope.mangopayBankOptions.length; i++) {
                if ($scope.mangopayBankOptions[i]['id'] == bankId) {
                    $scope.mangopaySwift = $scope.mangopayBankOptions[i]['swift'];
                    $scope.mangopayIban = $scope.mangopayBankOptions[i]['iban'];
                    $scope.mangopayNumber = $scope.mangopayBankOptions[i]['number'];
                    $scope.mangopayAddress = $scope.mangopayBankOptions[i]['address'];
                    $scope.mangopayZip = $scope.mangopayBankOptions[i]['zip'];
                    $scope.mangopayCity = $scope.mangopayBankOptions[i]['city'];
                    $scope.mangopayCountry = $scope.mangopayBankOptions[i]['country'];
                    break;
                }
            }
        };


        $scope.entity.support_charity = function(obj) {
            EntityService.assign_role(obj.slug, 2).then(function(item) {
                if (item.success == true) {
                    $scope.entity.supported_charities.push(obj);
                    obj.supported = true;
                    $scope.entity.supported_charities_total += 1;
                }
            });
        };

        $scope.entity.stop_support_charity = function(obj) {
            EntityService.delete_role(obj.slug, 2).then(function(item) {
                if (item.success == true) {
                    for (var i = $scope.entity.supported_charities.length - 1; i >= 0; i--) {
                        if ($scope.entity.supported_charities[i] === obj) {
                            $scope.entity.supported_charities.splice(i, 1);
                        }
                    }
                    $scope.entity.supported_charities_total -= 1;
                }
            });
        };


        $scope.entity.remove_partner = function(obj) {
            EntityService.delete_role($scope.entity.slug, 3, obj.slug).then(function(item) {
                if (item.success == true) {
                    for (var i = $scope.entity.partners.length - 1; i >= 0; i--) {
                        if ($scope.entity.partners[i] === obj) {
                            $scope.entity.partners.splice(i, 1);
                        }
                    }
                    $scope.entity.partners_total -= 1;
                }
            });
        };



        $scope.entity.remove_sponsor = function(obj) {
            EntityService.delete_role($scope.entity.slug, 3, obj.slug).then(function(item) {
                if (item.success == true) {
                    for (var i = $scope.entity.partners.length - 1; i >= 0; i--) {
                        if ($scope.entity.partners[i] === obj) {
                            $scope.entity.partners.splice(i, 1);
                        }
                    }
                    $scope.entity.partners_total -= 1;
                }
            });
        };

        $scope.entity.remove_member = function(obj) {
            EntityService.delete_role($scope.entity.slug, 1, obj.slug).then(function(item) {
                if (item.success == true) {
                    for (var i = $scope.entity.members.length - 1; i >= 0; i--) {
                        if ($scope.entity.members[i] === obj) {
                            $scope.entity.members.splice(i, 1);
                        }
                    }
                    $scope.entity.members_total -= 1;
                }
            });
        };

        $scope.entity.remove_admin = function(obj) {
            EntityService.delete_role($scope.entity.slug, 0, obj.slug).then(function(item) {
                if (item.success == true) {
                    for (var i = $scope.entity.admins.length - 1; i >= 0; i--) {
                        if ($scope.entity.admins[i] === obj) {
                            $scope.entity.admins.splice(i, 1);
                        }
                    }
                    $scope.entity.admins_total -= 1;
                }
            });
        };

        $scope.friends_search = function() {
            EntityService.search_entity($scope.entity.friend_search_input).then(function(item) {
                $scope.entity.search_result = item.objects;
            });
        };

        $scope.charities_search = function() {
            EntityService.search_entity($scope.entity.charities_search_input, ['charity']).then(function(item) {
                $scope.entity.charity_search_result = item.objects;
            });
        };

        $scope.entity.invite_member = function(obj) {
            EntityService.invite($scope.entity.slug, obj.slug, null, 1).then(function(item) {
                if (item.success == true) {
                    obj.invites.member = true;
                }
            });
        };

        $scope.entity.invite_admin = function(obj) {
            EntityService.invite($scope.entity.slug, obj.slug, null, 0).then(function(item) {
                if (item.success == true) {
                    obj.invites.administrator = true;
                }
            });
        };

        $scope.entity.invite_partner = function(obj) {
            EntityService.invite($scope.entity.slug, obj.slug, null, 3).then(function(item) {
                if (item.success == true) {
                    obj.invites.supporter = true;
                }
            });
        };

        $scope.members_search = function() {
            EntityService.search_entity($scope.entity.members_search_input, ['user'], {
                exclude_entity: $scope.entity.slug,
                excludes_list: ['members']
            }).then(function(item) {
                $scope.entity.members_search_result = item.objects;
            });
        };

        $scope.admins_search = function() {
            EntityService.search_entity($scope.entity.admins_search_input, ['user'], {
                excludes_list: ['admins']
            }).then(function(item) {
                $scope.entity.admins_search_result = item.objects;
            });
        };

        $scope.users_search = function(event, models, exclude_group) {
            $scope.invite_group = exclude_group;
            EntityService.search_entity('',
                models, {
                    exclude_entity: $scope.entity.slug,
                    excludes_list: [exclude_group]
                },
                true).then(function(item) {
                $scope.entity.show_all_users = item.objects;
                $scope.entity.users_total = item.total;
            });
            var d = ngDialog.open({
                template: '/static/js/apps/templates/popups/all_users.html',
                className: 'ngdialog-donationroad popup-wrapper popup-angular users-list',
                scope: $scope
            });
        };

        $scope.partners_search = function() {
            EntityService.search_entity($scope.entity.partners_search_input, ['user', 'company', 'charity'], {
                exclude_entity: $scope.entity.slug,
                excludes_list: ['supporters']
            }).then(function(item) {
                $scope.entity.partners_search_result = item.objects;
            });
        };

        $scope.check_partner = function(partnerId) {
            for (var i = 0; i < $scope.entity.partners.length; i++) {
                if ($scope.entity.partners[i]['id'] == partnerId) {
                    return true;
                }
            }
            return false;
        };

        $scope.invoice_payment = function(invoiceId) {
            EntityService.invoice_payment(invoiceId).then(function(item) {
                window.location.reload();
            });
        };

        $scope.closeSearchResult = function(group) {
            //Friends
            if ($scope.entity.friend_search_input && group == 'friends') {
                $scope.entity.friend_search_input = '';
                $scope.entity.search_result = [];
            }
            //Admins
            if ($scope.entity.admins_search_input && group == 'admins') {
                $scope.entity.admins_search_input = '';
                $scope.entity.admins_search_result = [];
            }
            //Team members
            if ($scope.entity.members_search_input && group == 'members') {
                $scope.entity.members_search_input = '';
                $scope.entity.members_search_result = [];
            }
            //Partners
            if ($scope.entity.partners_search_input && group == 'partners') {
                $scope.entity.partners_search_input = '';
                $scope.entity.partners_search_result = [];
            }

        };

        $scope.$watch('entity.friend_search_input', function(value) {
            if ($.trim(value).length > 1) {
                $scope.friends_search();
            } else
                $scope.entity.search_result = [];
        });

        $scope.$watch('entity.people.active_tab', function(val) {
            if (val == 'following') {
                $scope.entity.people_list = $scope.entity.following;
            } else if (val == 'followers') {
                $scope.entity.people_list = $scope.entity.followers;
            } else if (val == 'members') {
                $scope.entity.people_list = $scope.entity.members;
            }
        });

        $scope.$watch('entity.charities.active_tab', function(val) {
            if (val == 'owned') {
                $scope.entity.charities_list = $scope.entity.owned_charities;
            } else if (val == 'supported') {
                $scope.entity.charities_list = $scope.entity.supported_charities;
            }
        });

        $scope.$watch('entity.active_tab', function(val) {
            if (val == 'wall') {
                $rootScope.$broadcast('masonry.reload');
            }
        });

        $.extend(true, $scope, initial_data['data']);
        $.extend(true, $scope, initial_data['persist']);
    }
]);

