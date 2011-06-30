/**
 * @author Chris Yap
 * 	Flowgram Login Pane Controller
 */

var LoginController = Class.create();

Object.extend(LoginController.prototype, {
	initialize: function(){
		
		// set method caches
		this.openPaneCache = this.openPane.bindAsEventListener(this);
		this.closePaneCache = this.closePane.bindAsEventListener(this);
		this.handleEnterKeyCache = this.handleEnterKey.bindAsEventListener(this);
		
		// set click events to open and close login pane
		this.setClickEvents();
		
		// check to see if errors exist, if so, display login pane
		this.handleErrors();
		
	},
	
	// set click events to open and close login pane
	setClickEvents: function(){
		
		Event.observe($('login_pane_sign_in'), 'click', this.openPaneCache);
		Event.observe($('login_pane_btn_close_login'), 'click', this.closePaneCache);		
	
	},
	
	// set IE keypress events for enter key submit
	handleEnterKey: function() {
		checkEnter(event, $('login'));
	},
	
	openPane: function() {
		new Effect.Appear('wrapper_login', {duration: .3});
		setTimeout("$('id_username').focus()", 500);
		if (sniff_br_id == 'msie') {
			Event.observe($('id_username'), 'keypress', this.handleEnterKeyCache);
			Event.observe($('id_password'), 'keypress', this.handleEnterKeyCache);
		}
		pageTracker._trackPageview('/login/login_pane_open');
	},
	
	closePane: function() {
		new Effect.Fade('wrapper_login', {duration: .3});
		if (sniff_br_id == 'msie') {
			Event.stopObserving($('id_username'), 'keypress', this.handleEnterKeyCache);
			Event.stopObserving($('id_password'), 'keypress', this.handleEnterKeyCache);
		}
		pageTracker._trackPageview('/login/login_pane_close');
	},
	
	// check to see if errors exist, if so, display login pane
	handleErrors: function(){
		
		if ((($('wrapper_login').getElementsByClassName('errorlist')[0] != '') && ($('wrapper_login').getElementsByClassName('errorlist')[0] != null))) {
			$('wrapper_login').style.display = 'block';
			setTimeout("$('id_username').focus()", 500);
			if (sniff_br_id == 'msie') {
				Event.observe($('id_username'), 'keypress', this.handleEnterKeyCache);
				Event.observe($('id_password'), 'keypress', this.handleEnterKeyCache);
			}
		}
		
		if (($('wrapper_login').getElementsByClassName('errorlist')[0] != '') && ($('wrapper_login').getElementsByClassName('errorlist')[0] != null)) {
			setTimeout("pageTracker._trackPageview('/login/login_pane_user_error')", 5000);
		}
		
	}
	
	
});