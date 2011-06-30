/**
 * @author Chris Yap
 * 	Flowgram Context Edit Controller
 */

var ContextEditController = Class.create();

Object.extend(ContextEditController.prototype, {
	initialize: function(){ 
		
		// get all context edit forms on page
		this.initForms();
		
	},
	
	// get all context edit forms on page
	initForms: function(){
		
		// loop through and get all editable data into memory
		this.context_wrapper_divs = document.getElementsByClassName('wrapper_editable_data');
		for (var i=0; i < this.context_wrapper_divs.length; i++) {
			this.data_input = '';
			this.data_textarea = '';
			this.data_hidden = '';
			this.data_display = this.context_wrapper_divs[i].getElementsByClassName('editable_data_display')[0];
			if (this.context_wrapper_divs[i].getElementsByClassName('editable_data_input')[0] != null) {
				this.data_container = this.context_wrapper_divs[i].getElementsByClassName('editable_data_input')[0];
			}
			if (this.context_wrapper_divs[i].getElementsByClassName('editable_data_textarea')[0] != null) {
				this.data_container = this.context_wrapper_divs[i].getElementsByClassName('editable_data_textarea')[0];
			}
			if (this.context_wrapper_divs[i].getElementsByClassName('editable_data_select')[0] != null) {
				this.data_container = this.context_wrapper_divs[i].getElementsByClassName('editable_data_select')[0];
			}
			if (this.context_wrapper_divs[i].getElementsByClassName('editable_data_hidden')[0] != null) {
				this.data_hidden = this.context_wrapper_divs[i].getElementsByClassName('editable_data_hidden')[0];
			}
			this.data_form = this.context_wrapper_divs[i].getElementsByTagName('form')[0];
			this.data_buttons = this.context_wrapper_divs[i].getElementsByClassName('editable_data_buttons')[0];
			this.data_submit = this.context_wrapper_divs[i].getElementsByClassName('editable_data_submit')[0];
			this.data_cancel = this.context_wrapper_divs[i].getElementsByClassName('editable_data_cancel')[0];
			this.data_loading = this.context_wrapper_divs[i].getElementsByClassName('editable_data_loading')[0];
			this.setFormEvents(this.data_display, this.data_container, this.data_form, this.data_submit, this.data_cancel, this.data_loading, this.data_hidden, this.data_buttons);
		};
		
		// find tag LI elements
		if ($('tags_list')) {
			if (($('tags_list').getElementsByTagName('li')[0] != null) && !($('tags_empty'))) {
				this.tag_elements = $('tags_list').getElementsByTagName('li');
				for (var i=0; i < this.tag_elements.length; i++) {
					this.tag_removal_link = Element.select(this.tag_elements[i], '[class="delete_tag"]')[0];
                    if (this.tag_removal_link) {
                        this.setTagRemovalEvents(this.tag_elements[i], this.tag_removal_link);
                    }
				}
			}
		}
		
	},
	
	// set events
	setFormEvents: function(data_display, data_container, data_form, data_submit, data_cancel, data_loading, data_hidden, data_buttons){
		
		// set context edit style indicator mouseover event
		if (Element.hasClassName(data_display, 'in_place')) {
			Event.observe(data_display, 'mouseover', function()
			{
				Element.addClassName(this.item_display, 'context_edit_indicator');
			}
			.bindAsEventListener({obj:this, item_display:data_display}));
		}
		

		// set context edit style indicator mouseout event
		if (Element.hasClassName(data_display, 'in_place')) {
			Event.observe(data_display, 'mouseout', function()
			{
				Element.removeClassName(this.item_display, 'context_edit_indicator');
			}
			.bindAsEventListener({obj:this, item_display:data_display}));
		}
		
		// set event to turn on init a context edit
		Event.observe(data_display, 'click', function()
		{
			this.item_form.style.display = 'block';
			this.item_display.style.display = 'none';
			
			// handle analytics
			pageTracker._trackPageview('/context_edit/init');
		}
		.bindAsEventListener({obj:this, item_display:data_display, item_form: data_form, item_container: data_container}));
		
		// set event to handle form submission
		Event.observe(data_form, 'submit', function()
		{
			this.item_loading.style.display = 'block';
			if (data_buttons.getElementsByClassName('error')[0]) {
				errors_array = data_buttons.getElementsByClassName('error');
				for (var i=0; i < errors_array.length; i++) {
					data_buttons.removeChild(errors_array[i]);
				}
			}
			
			// handle analytics
			pageTracker._trackPageview('/context_edit/submit');
			
			// check for emtpy data in tags, check and clean tags before submitting
			if (data_form.id == 'add_tag') {
				
				// check for empty submission
				if (data_container.value == '') {
					var message_text = 'You cannot enter an empty value for ' + data_container.name;
					smc.insertMessage(message_text);
					data_loading.style.display = 'none';
					return false;
				}
				
				// check for comma delimited data, clean if necessary and submit request for each tag separately
				else {
					tags = this.item_container.value;
					if (tags.indexOf(',') >= 0) {
						tags = tags.replace(/ /,"");
						tags_array = tags.split(",");
						var temp_input = document.createElement('input');
						temp_input.name = this.item_container.name;
						temp_input.type = 'hidden';
						temp_input.id = 'tags_temp';
						for (var i=0; i < tags_array.length; i++) {
							temp_input.value = tags_array[i];
							this.item_form.appendChild(temp_input);
							this.submitForm(this.item_display, $('tags_temp'), this.item_form, this.item_loading, this.item_hidden, this.item_buttons);
							this.item_form.removeChild($('tags_temp'));
						}
						
					}
					
					else {
						this.submitForm(this.item_display, this.item_container, this.item_form, this.item_loading, this.item_hidden, this.item_buttons);
					}
				}
			}
			
			else {
				this.submitForm(this.item_display, this.item_container, this.item_form, this.item_loading, this.item_hidden, this.item_buttons);
			}
		}
		.bindAsEventListener({obj:this, item_display:data_display, item_container:data_container, item_form:data_form, item_loading:data_loading, item_hidden:data_hidden, item_buttons:data_buttons, submitForm:this.submitForm}));
		
		// set event to handle cancel button click
		Event.observe(data_cancel, 'click', function()
		{
			//Effect.Appear(this.item_display,{duration:.5});
			this.item_display.style.display = 'block';
			this.item_form.style.display = 'none';
			Element.removeClassName(this.item_display, 'context_edit_indicator');
			if (data_buttons.getElementsByClassName('error')[0]) {
				errors_array = data_buttons.getElementsByClassName('error');
				for (var i=0; i < errors_array.length; i++) {
					data_buttons.removeChild(errors_array[i]);
				}
			}
			
			// handle analytics
			pageTracker._trackPageview('/context_edit/cancel');
		}
		.bindAsEventListener({obj:this, item_display:data_display, item_form: data_form}));
		
		// set event to handle textarea maxlengths
		if (data_container.type == 'textarea') {
			Event.observe(data_container, 'keyup', function()
			{
				var mlength=this.item_container.getAttribute? parseInt(this.item_container.getAttribute("maxlength")) : ""
				if (this.item_container.getAttribute && this.item_container.value.length>mlength)
				this.item_container.value=this.item_container.value.substring(0,mlength)
			}
			.bindAsEventListener({obj:this, item_container: data_container}));
		}
		
	},
	
	// submit a context edit form
	submitForm: function(data_display, data_container, data_form, data_loading, data_hidden, data_buttons) {
		
		this.form_action = data_form.action;
		this.pars = {};
		this.pars['csrfmiddlewaretoken'] = $('csrf_token').innerHTML;
		pars_name = data_container.name;
		pars_value = data_container.value;
		this.pars[pars_name] = pars_value;
		if (data_hidden != '') {
			pars_hidden_name = data_hidden.name;
			pars_hidden_value = data_hidden.value;
			this.pars[pars_hidden_name] = pars_hidden_value;
			if(data_hidden.name = 'flowgram_id') {
				var flowgram_id = pars_hidden_value;
			}
		}
		
		empty_value = '<span class="note">(<span class="click_to_edit">add ' + data_container.name + '</span>)</span>';
		
		this.context_edit_post = new Ajax.Request(this.form_action, 
		{
			asynchronous: true,
			method: 'POST', 
			parameters: this.pars,
			onComplete: function(transport)
					{
						
						// case for editing data items to be added to a list of existing data
						if ((data_form.id == 'add_comment') || (data_form.id == 'add_tag')) {
							
							data_container.value = '';
							
							// case for adding comment
							if (data_form.id == 'add_comment') {
								
								// parse xml
                                var value = eval(['(', transport.responseText, ')'].join('')).body;
								
								// set data from xml
								this.comment_text = value.text.escapeHTML();
								this.comment_date = value.timeAgo + ' ago';
								this.comment_avatar_src = value.ownerAvatar;
								this.comment_username = value.ownerUsername;
								this.comment_id = value.id;
								
								// build comment and insert into DOM
								this.comments_container = document.createElement('div');
								Element.addClassName(this.comments_container, 'row');
								this.avatar = document.createElement('img');
								this.avatar.src = this.comment_avatar_src;
								Element.addClassName(this.avatar, 'avatar');
								this.info_div = document.createElement('div');
								Element.addClassName(this.info_div, 'info');
								this.user_link = '/' + this.comment_username;
                                var username = '';
                                if (this.comment_username != 'Anonymous') {
                                    username = '<a href="' + this.user_link + '/">' + this.comment_username + '</a>';
                                } else {
                                    username = 'Anonymous';
                                }
								this.info_div.innerHTML = '<strong>' + username + ' says:</strong><br/>' + this.comment_text + '<br/><span class="date">Posted ' + this.comment_date + '</span>';
								if (owns_page == true) {
									this.info_div.innerHTML += ' (<a href="/delcomment/' + this.comment_id + '/">delete</a>)';
								}
								this.clearer_div = document.createElement('div');
								Element.addClassName(this.clearer_div, 'clearer');
								this.comments_container.appendChild(this.avatar);
								this.comments_container.appendChild(this.info_div);
								this.comments_container.appendChild(this.clearer_div);
								$('wrapper_comments').appendChild(this.comments_container);
								new Effect.Highlight(this.comments_container,{duration:2, endcolor:'#E1F1F5'});
								
								// remove no comments message if it exists
								if ($('comments_empty')) {
									$('wrapper_comments').removeChild($('comments_empty'));
								}
								
								// handle analytics
								pageTracker._trackPageview('/context_edit/add_comment');
								
								
							}
							
							// case for adding tag
							if (data_form.id == 'add_tag') {
								tag_value = transport.responseText;
								tag_url = '/tags/' + tag_value;
								tag_url_remove = '/fg/' + flowgram_id + '/deletetag/' + tag_value + '/';
								new_data_container = document.createElement('li');
								new_data_link = document.createElement('a');
								new_data_link_remove = document.createElement('a');
								new_data_link.href = tag_url;
								Element.addClassName(new_data_link_remove, 'delete_tag');
								new_data_link_remove.href = tag_url_remove;
								new_data_link_remove.onclick = function(){
									return false;
								}
								new_data_link.innerHTML = tag_value + ' ';
								new_data_link_remove.innerHTML = '[x]';
								$('tags_list').appendChild(new_data_container);
								new_data_container.appendChild(new_data_link);
								new_data_container.appendChild(new_data_link_remove);
								new Effect.Highlight(new_data_container,{duration:2});
								
								// remove the no results message if adding the first tag
								if($('tags_empty')){
									$('tags_list').removeChild($('tags_empty'));
								}
								
								// set event on new elements for ajax tag removal
								cec.setTagRemovalEvents(new_data_container, new_data_link_remove);
								
								// handle analytics
								pageTracker._trackPageview('/context_edit/add_tag');
								
							}
							
						}
						
						// case for editing data items in place
						else {
							
							// set response
							response_container = transport.responseText;
							
							// case for birthdate and homepage fields - check response for errors
							if ((data_container.name == 'birthdate') || (data_container.name == 'homepage') || (data_container.name == 'email')) {
																							
							    re = '((?:[a-z][a-z]+))';
							    p = new RegExp(re,["i"]);
							    m = p.exec(response_container);
								
								if (m[1] == 'VALID') {
									response_container = response_container.replace(/VALID\s/, '');
									
									// handle analytics
									if (data_container.name == 'birthdate') {
										pageTracker._trackPageview('/context_edit/edit_birthdate');
									}
									else if (data_container.name == 'homepage') {
										pageTracker._trackPageview('/context_edit/edit_homepage');
									}
									else if (data_container.name == 'email') {
										pageTracker._trackPageview('/context_edit/edit_email');
									}
								}

								else if (m[1] == 'ERROR') {
									data_loading.style.display = 'none';
									response_container = response_container.replace(/ERROR\s/, '');
									error_container = document.createElement('div');
									Element.addClassName(error_container, 'error');
									error_container.innerHTML = response_container;
									data_buttons.appendChild(error_container);
									
									// handle analytics
									if (data_container.name == 'birthdate') {
										pageTracker._trackPageview('/context_edit/invalid_birthdate');
									}
									else if (data_container.name == 'homepage') {
										pageTracker._trackPageview('/context_edit/invalid_homepage');
									}
									else if (data_container.name == 'email') {
										pageTracker._trackPageview('/context_edit/invalid_email');
									}
									
									return false;
								}
							}
							
							// place response into DOM
							if (pars_value != '') {
								data_display.innerHTML = response_container;
								if ((data_form.id == 'add_description') || (data_form.id == 'add_title')) {
									data_display.innerHTML += ' <span class="note">(<span class="click_to_edit">click to edit</span>)</span>';
								}
								Element.removeClassName(data_display, 'empty_value');
							}
							else {
								data_display.innerHTML = empty_value;
								Element.addClassName(data_display, 'empty_value');
							}
							new Effect.Highlight(data_display,{duration:2, endcolor:'#E1F1F5'});
						}															

						// display data and turn context edit form back off
						data_form.style.display = 'none';
						data_display.style.display= 'block';
						data_loading.style.display = 'none';
					}
		});
	},

	// set tag removal events
	setTagRemovalEvents: function(tag_element, tag_removal_link){

		// set event to turn on init a context edit
		Event.observe(tag_removal_link, 'click', function()
		{
			var tag_removal_window = document.createElement('iframe');
			tag_removal_window.id = 'tag_removal_window';
			tag_removal_window.src = tag_removal_link.href;
			document.body.appendChild(tag_removal_window);
			$('tag_removal_window').onload = function() {
                document.body.removeChild(tag_removal_window);
			}
			
			$('tags_list').removeChild(this.item_tag);
			
			// add the no results message back if removing the last tag
			if($('tags_list').getElementsByTagName('li')[0] == null){
				empty_message = document.createElement('li');
				empty_message.id = 'tags_empty';
				empty_message.innerHTML = 'There are no tags for this Flowgram.'
				$('tags_list').appendChild(empty_message);
			}
			
			// handle analytics
			pageTracker._trackPageview('/context_edit/remove_tag');
		}
		.bindAsEventListener({obj:this, item_tag:tag_element}));

	},
	
	handlePrivacyForm: function() {
		
		this.privacy_form_action = $('privacy_form').action;
		
		Event.observe($('make_public'), 'click', function()
		{
			this.privacyFormSubmit(true);
		}
		.bindAsEventListener(this));
		
		Event.observe($('make_private'), 'click', function()
		{
			this.privacyFormSubmit(false);
		}
		.bindAsEventListener(this));
		
	},
	
	privacyFormSubmit: function(public_setting) {
		
		var csrf_token = '&csrfmiddlewaretoken=' + $('csrf_token').innerHTML;
		this.privacy_form_submit = new Ajax.Request(this.privacy_form_action, 
		{
			asynchronous:true,
			method:'POST', 
			parameters:'public=' + public_setting + '&flowgram_id=' + $('privacy_form_flowgram_id').value + csrf_token,
			onComplete: function()
			{
				setTimeout("smc.insertMessage('The privacy settings for this Flowgram have been changed.')", 500);
			}.bindAsEventListener(this)
		});
	}
	
	
});
