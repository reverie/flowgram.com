/**
 * @author Chris Yap
 * 	Flowgram Toolbar/Bookmarklet Install Controller
 */

var InstallController = Class.create();

Object.extend(InstallController.prototype, {
	initialize: function(){
		
		if (!(sniff_br_id == 'firefox') && !(sniff_br_id == 'safari') && !(sniff_br_id == 'msie')) {
			return false;
		}
		
		this.setEvents();
		image_array = new Array('/media/images/bg_help_bubble.png');
		preloadImages(image_array);
		
		if (sniff_br_id == 'firefox') {
            if (sniff_major_version == 2) {
                $('firefox_express').style.display = 'block';
            }
			this.handleTutorial();
		}
		
		
		if (sniff_br_id == 'safari') {
			this.handleTutorial();
		}
		
	},
	
	setEvents: function() {
		
		if (sniff_br_id == 'msie') {
			this.bookmarklet_links = $('IE_bookmarklet_links').select('a[class="bookmarklet"]');
			this.bookmarklet_help_bubble = $('IE_manual').select('div[class="help_bubble"]')[0];
		}
		
		else if ((sniff_br_id == 'firefox') || (sniff_br_id == 'safari')) {
			this.bookmarklet_links = $('firefox_bookmarklet_links').select('a[class="bookmarklet"]');
			this.bookmarklet_help_bubble = $('firefox_bookmarklet_links').select('div[class="help_bubble"]')[0];
		}
		
		this.bookmarklet_help_bubble_on_cache = this.bookmarkletHelpBubbleOn.bindAsEventListener(this);
		this.bookmarklet_help_bubble_off_cache = this.bookmarkletHelpBubbleOff.bindAsEventListener(this);
		
		for (var i=0; i < this.bookmarklet_links.length; i++) {
			// set click event to pop help bubble
			Event.observe(this.bookmarklet_links[i], 'click', this.bookmarklet_help_bubble_on_cache);
		}

	},
	
	unsetEvents: function() {
		for (var i=0; i < this.bookmarklet_links.length; i++) {
			// unset mouseover event
			Event.stopObserving(this.bookmarklet_links[i], 'click', this.bookmarklet_help_bubble_on_cache);
			
			// unset mouseout event
			Event.stopObserving(this.bookmarklet_links[i], 'click', this.bookmarklet_help_bubble_off_cache);
		}
	},
	
	bookmarkletHelpBubbleOn: function() {
		this.bookmarklet_help_bubble.style.display = 'block';
	},
	
	bookmarkletHelpBubbleOff: function() {
		this.bookmarklet_help_bubble.style.display = 'none';
	},
	
	handleManualClick: function() {
		
		new Effect.Appear($('IE_manual'), {duration: .3});
		
	},
	
	handleTutorial: function() {
		
		this.iframe_string = '<iframe id="tutorial_iframe" frameborder="0" scrolling="no" width="345" height="315"></iframe>'
		this.firefox_tutorial_path = '/media/swf/tutorials/createfirefoxpaused022608/createfirefoxpaused022608.html';
		this.tutorial_path = this.firefox_tutorial_path;
		$('firefox_video').innerHTML = this.iframe_string;
		$('tutorial_iframe').src = this.firefox_tutorial_path;
		
	}
	
	
	
});