donationRoad.directive('imgCropped', function() {
    return {
        restrict: 'E',
        replace: true,
        scope: { src:'@', initial:'@', aspectratio: '@', fitto:'@', selected:'&'},
        link: function(scope,element, attr) {
            var myImg;
            var clear = function() {
                if (myImg) {
                    myImg.next().remove();
                    myImg.remove();
                    myImg = undefined;
                }
            };
            scope.$watch('src', function(nv) {
                clear();
                if (nv) {
                    element.after('<img />');
                    myImg = element.next();
                    $(myImg).hide();
                    myImg.attr('src',nv);

                    var temp = new Image();
                    temp.src = nv;
                    temp.onload = function() {
                        var width = this.width;
                        var height = this.height;
                        var wrong_params = [null, '', undefined];

                        if (wrong_params.indexOf(scope.aspectratio)==-1) {
                                var ratio_w = 1;
                                var ratio_h = 1;
                                if (scope.aspectratio.indexOf('/')!=-1) {
                                    ratio_w = parseInt(scope.aspectratio.split('/')[0]);
                                    ratio_h = parseInt(scope.aspectratio.split('/')[1]);
                                }
                                var ratio = ratio_w/ratio_h;
                            }

                        if (wrong_params.indexOf(scope.initial)!=-1) {

                        	if (wrong_params.indexOf(scope.aspectratio)==-1) {
                    			var x = 0, y = 0;
                    			var x_ = width, y_ = height;

								var x_r = (x_ / ratio) - y_;
								var y_r = (y_ / ratio) - x_;

								if (x_r > 0) {
								    x = (x_r/ 2)+Math.round(height/20);
								    x_= height-(Math.round(height/20)*2);
								}
								else {
									x = x+Math.round(width/20);
									x_=width-Math.round(width/20);
								}

								if (y_r > 0) {
								    y = (y_r / 2)+Math.round(width/20);
								    y_ = width-(Math.round(width/20)*2);
								}
								else {
									y = y+Math.round(height/20);
									y_=height-Math.round(height/20);
								}

								scope.initial = [x, y, x_, y_];


                    		} else {

                        	var dw = width-Math.round(width/20);
                        	var dh = height-Math.round(height/20);
                        	var x = width/2-dw/2;
                        	var y = height/2-dh/2;
                        	var x1 = x+dw;
                        	var y1 = y+dh;

                    		scope.initial = [x, y, x1, y1];
                    		}
                    	}
                    	else {
                    		scope.initial = JSON.parse(scope.initial);
                    	}
                    	var jcrop_options = {
                            trackDocument: true,
                            onSelect: function(x) {
                                scope.selected({coords:x});
                            },
                            boxWidth: $('#charity-wall-filelist').width(), boxHeight: 800,
                            setSelect: scope.initial,
                            trueSize: [width, height],
                            addClass: 'wall-img-preview'
                       };
                    	if (wrong_params.indexOf(scope.aspectratio)==-1) {
                    		jcrop_options.aspectRatio = ratio;
                        }
                    	if (wrong_params.indexOf(scope.fitto)==-1) {
                    		jcrop_options.boxWidth = $(scope.fitto).width();
                    		jcrop_options.boxHeight = $(scope.fitto).height();
                    	}

						$(myImg).css('margin-left',  Math.round($('#charity-wall-filelist').width()/2-width/2));
                        $(myImg).Jcrop(jcrop_options);
                        scope.initial = "";
                    };
                }
            });

            scope.$on('$destroy', clear);
        }
    };
});
