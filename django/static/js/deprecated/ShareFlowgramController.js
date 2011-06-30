/**
 * @author Chris Yap
 * 	Flowgram Website Share Controller
 */

var ShareFlowgramController = Class.create();

Object.extend(ShareFlowgramController.prototype, {
	initialize: function(){
	
		this.setElements();
		this.setEvents();
		this.setPermLink();
		image_array = new Array('/media/images/icons/email_grey.gif','/media/images/icons/facebook_grey.gif','/media/images/icons/chat_grey.gif');
		preloadImages(image_array);
		
	},
	
	// get page elements into memory
	setElements: function() {
		
		this.pref_items = $('share_preference_container').select('div[selector="pref"]');
		this.share_methods = $('wrapper_share_methods').select('div[selector="share_methods"]');
		this.email_module = $('share_email');
		this.email_form_container = $('share_email_form_container');
		this.email_form = $('share_email_form');
		this.email_flowgram_id = $('share_email_flowgram_id');
		this.email_recipients = $('share_email_recipients');
		this.email_message = $('share_email_message');
		this.email_send = $('share_email_send');
		this.link_input = $('share_link_input');
		
	},
	
	// set events
	setEvents: function() {
		
		// set rollover events on pref items
		for (var i=0; i < this.pref_items.length; i++) {
			
			Event.observe(this.pref_items[i], 'mouseover', function() {
				Element.addClassName(this.item, 'over');
			}
			.bindAsEventListener({obj:this, item:this.pref_items[i]}));
			
			Event.observe(this.pref_items[i], 'mouseout', function() {
				Element.removeClassName(this.item, 'over');
			}
			.bindAsEventListener({obj:this, item:this.pref_items[i]}));
		}
		
		// clear recipients field on focus
		Event.observe(this.email_recipients, 'focus', function() {
			this.email_recipients.value = '';
		}
		.bind(this));
		
		// set click event on email share send button
		Event.observe(this.email_send, 'click', function()
		{
			this.showLoadingGif();
			var check = false;
			check = this.validateEmails();
			if (check == true) {
				this.sendEmail(this.email_recipients.value);
			}
		}
		.bind(this));
		
		// select permanent link on focus
		Event.observe(this.link_input, 'focus', function() {
			this.link_input.select();
		}
		.bind(this));
		
	},

	setPermLink: function() {

		var domain = getDomain();
		this.perm_link = 'http://' + domain + '/fg/' + flowgram_id + '/';
		this.link_input.value = this.perm_link;

	},
	
	togglePrefs: function(selected_item) {
		
		var pref_tab = 'tab_' + selected_item;
		
		for (var i=0; i < this.pref_items.length; i++) {
			Element.removeClassName(this.pref_items[i], 'on');
		}
		
		Element.addClassName($(pref_tab), 'on');
		
		for (var i=0; i < this.share_methods.length; i++) {
			if (this.share_methods[i].hasClassName('on')) {
				new Effect.Fade(this.share_methods[i], {duration: .2});
			}
		}
		
		if (selected_item == 'email') {
			setTimeout(function() { new Effect.Appear('share_email', {duration: .3, queue: 'end'}) }.bind(this), 300);
			Element.addClassName($('share_email'), 'on');
		}
		
		else if (selected_item == 'facebook') {
			setTimeout(function() { new Effect.Appear('share_facebook', {duration: .3, queue: 'end'}) }.bind(this), 300);
			Element.addClassName($('share_facebook'), 'on');
		}
		
		else if (selected_item == 'chat') {
			setTimeout(function() { new Effect.Appear('share_link', {duration: .3, queue: 'end'}) }.bind(this), 300);
			Element.addClassName($('share_link'), 'on');
		}
		
	},
	
	validateEmails: function() {
		
		// get emails into an array
		var email_array = $w(this.email_recipients.value);
		
		// scrub commas out of emails
		var re = /,/g;
		for (var i=0; i < email_array.length; i++) {
			email_array[i] = email_array[i].replace(re,"");
		}
		
		for (var i=0; i < email_array.length; i++) {
			if (echeck(email_array[i]) == false) {
				//error
				this.createMessage('At least one of the emails you entered is not valid.', 'error');
				this.hideLoadingGif();
				return false;
			} 
		}
		
		return true;
		
	},
	
	// ajax send email
	sendEmail: function() {
		
		this.email_form.submit();
		
		
		// TODO(cyap) Turn this into an ajax request... code is commented out below
		
		/*
		this.form_action = this.email_form.action;
		this.pars = 'flowgram_id=' + flowgram_id + '&recipients=' + this.email_recipients.value + '&message=' + this.email_message.value;
		
		this.share_email_post = new Ajax.Request(this.form_action, 
			{
				asynchronous:true,
				method:'POST', 
				parameters:this.pars,
				onComplete: function(transport) {
					alert(transport.responseText);
				}
				
			});
		*/
		
	},
	
	handleFacebook: function(title) {
		window.open('http://www.facebook.com/sharer.php?u='+encodeURIComponent(this.perm_link)+'&t='+encodeURIComponent(title),'sharer','toolbar=0,status=0,width=626,height=436');
	},
	
	createMessage: function(message, style_class) {
		if(this.message_container) {
			this.email_module.removeChild(this.message_container);	
		}
		this.message_container = document.createElement('p');
		Element.addClassName(this.message_container, style_class);
		this.message_container.innerHTML = message;
		this.email_form_container.insert({ top: this.message_container });
		new Effect.Highlight(this.message_container,{duration: 5});
	},

	showLoadingGif: function() {
		$('share_email_loading').style.visibility = 'visible';
	},
	
	hideLoadingGif: function() {
		$('share_email_loading').style.visibility = 'hidden';
	}
	
	
});
