/**
 * @author Chris Yap
 * 	Flowgram Invite Controller
 */

var InviteController = Class.create();

Object.extend(InviteController.prototype, {
	initialize: function(){ 
		
		if (has_invites == 'true' && sniff_br_id == 'msie') {
			this.handleEnterKeyCache = this.handleEnterKey.bindAsEventListener(this);
			Event.observe($('invite_email'), 'keypress', this.handleEnterKeyCache);
		}
		
	},
	
	showPersonalBox: function(){
        var personal_message_box = $("personal_box");
	    personal_message_box.style.display = "block";
		var personal_link = $("personal_link");
	    personal_link.style.display = "none";		
	},
	
	// submit a context edit form
	submitForm: function(){
		
		// set vars
		this.invite_form = $('invite_form');
		this.form_action = this.invite_form.action;
		this.email_base = $('invite_email').name + '=';
		this.email_value = $('invite_email').value;
		this.message_base = '&'+$('personal_message_email').name + '=';
		this.message_value = $('personal_message_email').value;
		var csrf_token = '&csrfmiddlewaretoken=' + $('csrf_token').innerHTML;
		if (this.email_value == '') {
			return false;
		}

		this.pars = this.email_base + this.email_value + this.message_base + this.message_value + csrf_token;
		
		// validate email
		this.pars_validate = this.email_value.split(/\s*,\s*/);
		for (var i=0; i < this.pars_validate.length; i++) {
			var validate = echeck(this.pars_validate[i]);
			if (validate == false) {
				this.handleError('At least one of the emails you entered is not valid.');
				return false;
			}	
		}
		
		$('invite_loading').style.visibility = 'visible';
		
		// ajax submission
		this.invite_post = new Ajax.Request(this.form_action, 
		{
			asynchronous:true,
			method:'POST', 
			parameters:this.pars,
			onComplete: function(transport)
			{
				var value = eval(['(', transport.responseText, ')'].join(''));
                
                if (value.error) {
					this.handleError('An error occurred while trying to send your invitation(s).');
					$('invite_loading').style.visibility = 'hidden';
                } else {
					$('invite_email').value = '';
					$('invite_loading').style.visibility = 'hidden';
					smc.insertMessage('Invites successfully sent.');
					if ($('invite_error').innerHTML) {
						$('wrapper_invite_form').removeChild($('invite_error'));
					}
                }
			}.bind(this)	
		});
		
	},
	
	handleError: function(error_text) {
		
		if (this.error_message) {
			this.error_message.innerHTML = error_text;
			return false;
		}
		this.error_message = document.createElement('div');
		Element.addClassName(this.error_message, 'error');
		this.error_message.id = 'invite_error';
		this.error_message.innerHTML = error_text;
		Element.insert(this.invite_form, {before:this.error_message});
		return false;
		
	},
	
	// set IE keypress events for enter key submit
	handleEnterKey: function() {
		checkEnterManual(event, $('invite_form'));
		if (checkEnterManual == false) {
			this.submitForm();
		}
	}
	
	
});