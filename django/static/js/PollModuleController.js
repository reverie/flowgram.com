/**
 * @author Chris Yap
 * 	Flowgram Poll Module Controller
 */

var PollModuleController = Class.create();

Object.extend(PollModuleController.prototype, {
	initialize: function(){ 
		
		this.poll_form = $('poll_module_form');
		this.form_action = this.poll_form.action;
		this.poll_radios = Element.select(this.poll_form, 'input[class="poll_item"]');
		this.poll_id_base = 'poll_id=';
		this.poll_id = $('poll_id').value;
		
	},
	
	// submit a context edit form
	submitForm: function(){
		
		// set vars
		this.poll_cookie_name = 'flowgram_poll_' + this.poll_id;
		this.vote_base = '&vote_id=';
		for (var i=0; i < this.poll_radios.length; i++) {
			if (this.poll_radios[i].checked) {
				this.vote_value = this.poll_radios[i].value;
			}
		}
		var csrf_token = '&csrfmiddlewaretoken=' + $('csrf_token').innerHTML;
		this.pars = this.poll_id_base + this.poll_id + this.vote_base + this.vote_value + csrf_token;
		
		// ajax submission
		this.poll_post = new Ajax.Updater($('poll_module_content'), this.form_action, 
		{
			asynchronous:true,
			method:'POST', 
			parameters:this.pars,
			onComplete: function()
			{
				
				Cookie.set(this.poll_cookie_name, 'already_voted', 1, '/');
				
			}.bind(this)	
		});
		
	}
	
	
});