/**
 * @author Chris Yap
 * 	Flowgram Nav Controller
 */

var NavController = Class.create();

Object.extend(NavController.prototype, {
	initialize: function(){
		
		// init navigation
		this.initGlobalNav();
		
		// init paginator
		this.initPaginator();
		
		// preload nav images
		image_array = new Array('/media/images/nav/home_on.png','/media/images/nav/browse_on.png','/media/images/nav/create_on.png','/media/images/nav/you_on.png','/media/images/bg_smoke.png');
		preloadImages(image_array);
		
		// set body class
		//this.setBodyClass();
	},
	
	initGlobalNav: function() {
		
		// set global nav rollover events
		var topLevelNavArray = $('wrapper_nav_global').select('img[class="nav_item"]');
		for (var i=0; i < topLevelNavArray.length; i++) {
			
			this.rememberState = topLevelNavArray[i].src;
			
			// set mouseover event
			Event.observe(topLevelNavArray[i], 'mouseover', function()
			{
				this.image.src = this.image.src.replace(/_off/, "_on");
			}
			.bindAsEventListener({obj:this, image:topLevelNavArray[i]}));
			
			// set mouseout event
			Event.observe(topLevelNavArray[i], 'mouseout', function()
			{
				this.image.src = this.remember;
			}
			.bindAsEventListener({obj:this, image:topLevelNavArray[i], remember:this.rememberState}));
			
		};
		
	},
	
	initPaginator: function() {
		if ($('paginator_ul')) {
			var paginator_width = $('paginator_ul').offsetWidth;
			var paginator_margin = (520 - paginator_width) / 2;
			$('paginator_ul').style.marginLeft = paginator_margin + 'px';
			$('paginator_ul').style.visibility = 'visible';
		}
	}
	
	
});