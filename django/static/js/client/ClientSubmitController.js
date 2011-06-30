/**
 * @author Chris Yap
 * 	Flowgram Client Submit Controller
 */

var ClientSubmitController = Class.create();

Object.extend(ClientSubmitController.prototype, {
	initialize: function(){
		
		this.submit_button = document.getElementsByClassName('submit')[0];
		this.submit_action = document.forms[0].action;
		this.setEvents();
		
		
	},
	
	setEvents: function(){
		
		Event.observe(this.submit_button, 'click', function()
		{
			this.submitForm();
		}
		.bindAsEventListener(this));
		
	},
	
	submitForm: function(){
		
		this.pars = '';
		this.form_array = document.getElementsByTagName('input');
		for (var i=0; i < this.form_array.length; i++) {
			var input_name = this.form_array[i].name;
			var input_value = this.form_array[i].value;
			
			if (this.form_array[i].type == 'checkbox') {
				if(this.form_array[i].checked){
					var current_param_string = input_name + '=' + input_value;
				}
			}
			else {
				var current_param_string = input_name + '=' + input_value;
			}
			this.pars = this.pars + current_param_string;
			if (i < (this.form_array.length - 1)) {
				this.pars = this.pars + '&';
			}
		}
		
		this.client_submit = new Ajax.Request(this.submit_action, 
		{
			asynchronous:true,
			method:'POST', 
			parameters:this.pars,
			onComplete: function(transport)
			{
				
				// parse xml
				var xmlParent = transport.responseXML;
				var xml = XML.getRootNode(transport.responseXML);
				this.xml_array = $NL(xml.childNodes).elements();
				
				// set data from xml
				// check to see if it's a valid response.  if not, continue setting vars and return false, otherwise fire the callback;
				this.response_validity = this.xml_array[0].firstChild.data;
				if(this.response_validity != 0){					
					this.error_array_container = $NL(this.xml_array[3].childNodes).elements();
					var error_field = new Array();
					var error_message = new Array();
					for (var i=0; i < this.error_array_container.length; i++) {
						error_field[i] = $NL(this.error_array_container[i].childNodes).elements()[0].firstChild.data;
						error_message[i] = $NL(this.error_array_container[i].childNodes).elements()[1].firstChild.data;
					}
					
					// grab form and all inputs
					this.form_element = document.getElementsByTagName('form')[0];
					this.form_array = document.getElementsByTagName('input');
					
					// create generic error container
					this.generic_error_div = document.createElement('div');
					this.generic_error_div.id = 'generic_errors';
					Element.addClassName(this.generic_error_div, 'error');
					
					for (var i=0; i < error_field.length; i++) {
						
						var current_error_field = error_field[i];
						var current_error_message = error_message[i];
						
						// case for generic errors
						if (error_field[i] == '__all__') {
							this.generic_error_div.innerHTML = '<p>' + current_error_message + '</p>';
						}
						
						// case for field specific errors
						for (var x=0; x < this.form_array.length; x++) {
							if (this.form_array[x].name == current_error_field) {
								var error_div = document.createElement('div');
								Element.addClassName(error_div, 'error');
								error_div.innerHTML = current_error_message;
								this.form_element.insertBefore(error_div, this.form_array[x].parentNode);
							}
						}
						
					}
						

					
					return false;
				}
				
				// check to see which form this is and fire the appropriate callback in the parent
				if (document.forms[0].id == 'client_login') {
					parent.client_login_callback();
				}
				else if (document.forms[0].id == 'client_register') {
					parent.client_register_callback();
				}
			}
		});
		
	}
	
	
});