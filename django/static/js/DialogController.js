/**
 * @author Chris Yap
 * 	Flowgram Dialog Controller
 */

var DialogController = Class.create();

Object.extend(DialogController.prototype, {
	initialize: function(dialog_path){
		
		this.dialog_path = dialog_path;
		this.createBackdrop();
		
	},
	
	// set backdrop behind adobe dialog
	createBackdrop: function(){
		
		// create backdrop element
		this.backdrop_element = document.createElement('div');
		this.backdrop_element.id = 'backdrop';
		document.body.appendChild(this.backdrop_element);
		
		// create dialog content wrapper
		this.wrapper_backdrop_content = document.createElement('div');
		this.wrapper_backdrop_content.id = 'wrapper_backdrop_content';
		document.body.appendChild(this.wrapper_backdrop_content);
		
		// create dialog content div
		this.backdrop_content = document.createElement('div');
		this.backdrop_content.id = 'backdrop_content';
		this.wrapper_backdrop_content.appendChild(this.backdrop_content);
		
		// handle backdrop height
		this.handleBackdropResize();
		
		// set event to handle window resize and scroll
		this.resizeCache = this.handleBackdropResize.bindAsEventListener(this); // necessary to cache the function for proper unregistration later
		Event.observe(window, 'resize', this.resizeCache);
		Event.observe(window, 'scroll', this.resizeCache);
		
		this.populateBackdrop(this.dialog_form_path, this.dialog_title);
		
	},
	
	// populate backdrop content
	populateBackdrop: function(dialog_form_path, dialog_title){
		
		var contentUpdater = new Ajax.Updater(this.backdrop_content, this.dialog_path, 
		{
			method: 'GET',
			evalScripts: true,
			onComplete: function()
				{ 
					 
					new Effect.Appear($('dialog'),{duration:.5});
					var dialog_width = $('dialog').style.width;
					$('backdrop_content').style.width = dialog_width;
					
					var close_elements = $('dialog').select('[class="dialog_close"]');
					
					for (var i=0; i < close_elements.length; i++) {
						// set close button event
						Event.observe(close_elements[i], 'click', function()
						{
							this.removeBackdrop();
						}
						.bindAsEventListener(this));
					}
					
				}.bind(this)
		});
		
		// set dialog position based on viewport
		var viewport_y_offset = getScrollY();
		$('wrapper_backdrop_content').style.top = viewport_y_offset + 20 + 'px';
		
		
		
	},
	
	// remove backdrop
	removeBackdrop: function(){
		
		$('backdrop_content').removeChild($('dialog'));
		$('wrapper_backdrop_content').removeChild($('backdrop_content'));
		document.body.removeChild($('wrapper_backdrop_content'));
		document.body.removeChild($('backdrop'));
		
		// stop observing window resize and scroll
		Event.stopObserving(window, 'resize', this.resizeCache);
		Event.stopObserving(window, 'scroll', this.resizeCache);
		
	},
	
	// handle backdrop resize
	handleBackdropResize: function(){
		
		// set backdrop height
		var windowHeightBodyOffset = document.body.offsetHeight;
		var windowHeightViewport = document.viewport.getHeight();
		if (windowHeightBodyOffset >= windowHeightViewport) {
			var windowHeight = windowHeightBodyOffset;
		}
		
		else {
			var windowHeight = windowHeightViewport;
		}
		
		this.backdrop_element.style.height = windowHeight + 'px';
		
	}
	
});