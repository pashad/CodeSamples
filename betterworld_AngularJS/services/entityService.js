donationRoad.service('EntityService', function($http, $q, $rootScope) {

    this.like = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.like");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, "slug=" + entity_id, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.unlike = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.unlike");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, "slug=" + entity_id, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.follow = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.follow");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, "slug=" + entity_id, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.unfollow = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.unfollow");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, "slug=" + entity_id, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.change_mission = function(entity_id, mission) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.change_mission");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, "slug=" + encodeURIComponent(entity_id) + ';mission=' + encodeURIComponent(mission), headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.change_fundraiser_status = function(fundraiser_id, status) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.campaigns.xhr.change_fundraiser_status");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, $.param({
            'fundraiser_id': fundraiser_id,
            'status': status
        }), headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.collect_email = function(email, role) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.invites.collect_emails");;
        var headers = $http.defaults.headers.post;
        var data = {
            email: email,
            role: role
        };
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, $.param(data)).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };


    this.change_avatar = function(entity_id, avatar, crop) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.change_avatar");
        var headers = $http.defaults.headers.post;
        var formdata = "slug=" + encodeURIComponent(entity_id) +
            ';avatar=' + encodeURIComponent(avatar) +
            ';crop=' + encodeURIComponent(crop);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };


    this.toggle_fundraiser = function(entity_id, type) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.toggle_fundraiser");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        data = {
            charity_id: entity_id,
            type: type
        };
        return $http.post(url, $.param(data), headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };


    this.toggle_approve_fundraiser = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.toggle_approve_fundraiser");
        var headers = $http.defaults.headers.post;
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        data = {
            charity_id: entity_id
        };
        return $http.post(url, $.param(data), headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_friends = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.friends");
        var headers = $http.defaults.headers.post;
        var formdata = "slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_following = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.following");
        var headers = $http.defaults.headers.post;
        var formdata = "slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_followers = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.relationships.followers");
        var headers = $http.defaults.headers.post;
        var formdata = "slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_supported_charities = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.supported_charities");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_companies = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.companies");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_charities = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.charities");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_supporters = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.supporters");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_partners = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.partners");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_members = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.members");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.get_admins = function(entity_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.admins");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id);
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.assign_role = function(entity_id, role) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.assign");
        var headers = $http.defaults.headers.post;
        var formdata = "account_slug=" + encodeURIComponent(entity_id) + ';role_id=' + encodeURIComponent(role);
        if (this.assign_role.arguments.length > 2) {
            formdata += ';person_slug=' + encodeURIComponent(this.assign_role.arguments[2]);
        }
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, formdata, headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

    this.invite = function(entity_id, person, email, role_id) {
        var deferrer = $q.defer();
        var url = dutils.urls.resolve("$.accounts.xhr.roles.invite");
        var headers = $http.defaults.headers.post;
        var formdata = {
            account_slug: encodeURIComponent(entity_id),
            role: encodeURIComponent(role_id)
        };
        if (person != null) {
            formdata.person_slug = encodeURIComponent(person);
        }
        if (email != null) {
            formdata.email = encodeURIComponent(email);
        }
        headers['Content-Type'] = 'application/x-www-form-urlencoded';
        return $http.post(url, $.param(formdata), headers = headers).then(function(resp) {
            var result = resp.data;
            deferrer.resolve(result);
            return deferrer.promise;
        });
    };

});