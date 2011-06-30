/**
 * @author Chris Yap
 * 	Flowgram Client Microphone Setup Controller
 */

// TODO(cyap): is this deprecated?

var ClientMicSetupController = Class.create();

Object.extend(ClientMicSetupController.prototype, {
	initialize: function(){
		
		this.continue_button = $('mic_setup_continue');
		this.setEvents();
		
	},
	
	// set events for mic setup
	setEvents: function(){
		
		Event.observe(this.continue_button, 'click', function()
		{
			this.createBackdrop();
			parent.client_mic_setup_callback();
		}
		.bindAsEventListener(this));
		
	},
	
	// set backdrop behind adobe dialog
	createBackdrop: function(){
		
		// create backdrop element
		this.backdrop_element = document.createElement('div');
		this.backdrop_element.id = 'backdrop';
		document.body.appendChild(this.backdrop_element);
		
		// handle backdrop height
		this.handleBackdropResize();
		
		// set event to handle window resize
		Event.observe(window, 'resize', function()
		{
			this.handleBackdropResize();
		}
		.bindAsEventListener(this));
		
	},
	
	// handle backdrop resize
	handleBackdropResize: function(){
		
		// set backdrop height based on viewport size
		var windowHeight=getWindowHeight();
		this.backdrop_element.style.height = windowHeight + 'px';
		
		
	}
	
});