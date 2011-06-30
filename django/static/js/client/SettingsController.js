/**
 * @author Chris Yap
 * 	Flowgram Client Settings Panel Controller
 */

var SettingsController = Class.create();

Object.extend(SettingsController.prototype, {
	initialize: function(save_callback, close_panel, delete_tag_callback){
		
		// create panel wrapper
		this.settings_panel = document.createElement('div');
		this.settings_panel.id = 'wrapper_settings_panel';
		
		// insert panel into dom, initial display set to none
		this.settings_panel.style.display = 'none';
		document.body.appendChild(this.settings_panel);
		
		// create upper shadow border and append to panel
		this.shadow_div = document.createElement('div');
		Element.addClassName(this.shadow_div, 'top');
		this.settings_panel.appendChild(this.shadow_div);
		
		// create end clearer div
		this.end_clearer_div = document.createElement('div');
		Element.addClassName(this.end_clearer_div, 'clearer');
		this.settings_panel.appendChild(this.end_clearer_div);
		
		// create title description module
		this.createTitleDescriptionModule();
		
		// create permissions module
		this.createPermissionsModule();
		
		// create tags module
		this.createTagsModule();
		
		// create save button
		this.createSaveButton(save_callback);
		
		// create close button
		this.createCloseButton(close_panel);
		
		this.delete_tag_callback = delete_tag_callback;
	},
	
	createTitleDescriptionModule: function(){
		// create title and description module and append to panel
		this.title_description_module = this.createModuleAndHeader('title_description', 'Title and Description');
				
		// create title input field with containing div and append to module
		var div = document.createElement('div');
		this.title_field = document.createElement('input');
		this.title_field.name = 'title';
		this.title_field.id = 'settings_title';
		div.appendChild(this.title_field);
		this.title_description_module.appendChild(div);
		
		// create description textarea with containing div and append to module
		var div = document.createElement('div');
		this.description_field = document.createElement('textarea');
		this.description_field.name = 'desc';
		this.description_field.id = 'settings_description';
		div.appendChild(this.description_field);
		this.description_field.value = 'Enter a description here.';
		this.title_description_module.appendChild(div);
	},
	
	createPermissionsModule: function(){
		// create permissions module and append to panel
		this.permissions_module = this.createModuleAndHeader('settings_permissions', 'Permissions');
		
		// create editable by with containing div and append to module
		this.editable_by_div = document.createElement('div');
		this.editable_by_div.id = 'settings_editable_by';
		this.permissions_module.appendChild(this.editable_by_div);
		
			// create editable by label and append to containing div
			this.editable_by_label = document.createElement('label');
			this.editable_by_label.innerHTML = 'Editable By';
			this.editable_by_div.appendChild(this.editable_by_label);
			
			// create container div for editable by fields and append to containing div
			this.editable_by_fields_container = document.createElement('div');
			this.editable_by_fields_container.id = 'settings_editable_by_fields';
			this.editable_by_div.appendChild(this.editable_by_fields_container);
			
			// create clearer div and append
			var div = document.createElement('div');
			Element.addClassName(div, 'clearer');
			this.editable_by_div.appendChild(div);
		
		// create viewable by with containing div and append to module
		this.viewable_by_div = document.createElement('div');
		this.viewable_by_div.id = 'settings_viewable_by';
		this.permissions_module.appendChild(this.viewable_by_div);
		
			// create viewable by label and append to containing div
			this.viewable_by_label = document.createElement('label');
			this.viewable_by_label.innerHTML = 'Viewable By';
			this.viewable_by_div.appendChild(this.viewable_by_label);
			
			// create container div for viewable by fields and append to containing div
			this.viewable_by_fields_container = document.createElement('div');
			this.viewable_by_fields_container.id = 'settings_viewable_by_fields';
			this.viewable_by_div.appendChild(this.viewable_by_fields_container);
			
			// create clearer div and append
			var div = document.createElement('div');
			Element.addClassName(div, 'clearer');
			this.viewable_by_div.appendChild(div);
		
	},
	
	createTagsModule: function(){
		// create tags module and append to panel
		this.tags_module = this.createModuleAndHeader('settings_tags', 'Tags');
		
		// create tags content div and append to module
		this.tags_content = document.createElement('div');
		this.tags_content.id = 'settings_tags_content';
		this.tags_module.appendChild(this.tags_content);
		
		// create tags ul and append to content div
		this.tags_content_ul = document.createElement('ul');
		this.tags_content.appendChild(this.tags_content_ul);
		
		// create clearer div - li elements in the tags ul are floated
		var div = document.createElement('div');
		Element.addClassName(div, 'clearer');
		this.tags_content.appendChild(div);
		
		// create add tag link and set event to create new input
		this.add_tag_link = document.createElement('a');
		this.add_tag_link.innerHTML = 'Add a new tag';
		this.add_tag_link.href = 'javascript:void(0);';
		this.tags_module.appendChild(this.add_tag_link);
		Event.observe(this.add_tag_link, 'click', function()
		{
			var new_input = document.createElement('input');
			this.tags_module.insertBefore(new_input, this.add_tag_link);
			new_input.focus();
		}
		.bindAsEventListener({obj:this, tags_module:this.tags_module, add_tag_link:this.add_tag_link}));
		
	},
	
	// create save button, append to the tags module, and set click event onto it - this button should send all the data back to the flex app
	createSaveButton: function(save_callback){
		
		// create save button
		this.save_button = document.createElement('div');
		this.save_button.id = 'settings_save';
		this.tags_module.appendChild(this.save_button);
		
		// set click event
		Event.observe(this.save_button, 'click', function()
		{
            var tags = this.getNewTags();
            
            for(var i = 0; i < tags.length; i++) {
                if(tags[i].trim() == "") {
                    alert("Please enter a word for all of your new tag");
                    return;
                }
            }

            save_callback();
		}
		.bindAsEventListener(this));
		
	},
	
	// create close button, append to the panel, and set click event onto it
	createCloseButton: function(close_panel) {
        this.closeButton_ = document.createElement('div');
        Element.addClassName(this.closeButton_, 'closeButton');
        this.closeButton_.style.right = '5px';
        this.settings_panel.appendChild(this.closeButton_);
        this.closeButton_.observe('click', close_panel);
	},
	
	// create a module header and return element
	createModuleAndHeader: function(module_id, module_title){
		// create module and append to panel
		var module_div = document.createElement('div');
		Element.addClassName(module_div, 'module');
		module_div.id = module_id;
			
			// create header bar and append to module
			var header_div = document.createElement('div');
			Element.addClassName(header_div, 'hdr_bar');
			module_div.appendChild(header_div);
				
				// create header text and append to header bar
				var header_text = document.createElement('h3');
				header_text.innerHTML = module_title;
				header_div.appendChild(header_text);
				
				// create clearer div and append to header bar
				var clearer_div = document.createElement('div');
				Element.addClassName(clearer_div, 'clearer');
				header_div.appendChild(clearer_div);
				
		this.settings_panel.insertBefore(module_div, this.end_clearer_div);
		
		return module_div;
		
	},
	
	showSettingsPanel: function(ypos){
		this.settings_panel.style.left = '0px';
		this.settings_panel.style.top = ypos + 'px';
		this.settings_panel.style.display = 'block';
		
	},
	
	hideSettingsPanel: function(){
		
		this.settings_panel.style.display  = 'none';
		
	},
	
	clearTags: function(){
	    // clear tags content
	    this.tags_content.removeChild(this.tags_content_ul);
		this.tags_content_ul = document.createElement('ul');
	    
	    var new_tags_array = this.tags_module.getElementsByTagName('input');
	    // loop through and clear out inputs
		for (var i=new_tags_array.length-1; i >= 0; i--) {
			this.tags_module.removeChild(new_tags_array[i]);
		}
	},
	
	setTitle: function(title){
		//$('settings_title').value = title;
		this.title_field.value = title;
	},
	
	getTitle: function(){
		return this.title_field.value;
	},
	
	setDescription: function(description){
		this.description_field.value = description;
	},
	
	getDescription: function(){
		return this.description_field.value;
	},
	
	setTags: function(tags){
		this.clearTags();
		
		var clearer_div = this.tags_content.getElementsByTagName('div')[0];
		
		// make sure to insert new tags content before the clearer div, since li elements are floated
		this.tags_content.insertBefore(this.tags_content_ul, clearer_div);
		
		// loop through passed array and populate tags content
		for (var i=0; i < tags.length; i++) {
			var tag_li = document.createElement('li');
			var tag_span = document.createElement('span');
			tag_span.innerHTML = tags[i].escapeHTML();
			Element.addClassName(tag_span, 'tag_content');
			tag_li.appendChild(tag_span);
			this.tags_content_ul.appendChild(tag_li);
		}
		
		// default margin-bottom is zero, need to add a 10px bottom margin if adding tags content
		this.tags_content.style.marginBottom = 10 + 'px';
		
		// handle tag deletion
		this.handleDeleteTags();
	},

    getExistingTags: function(){
        var existingTags = new Array();

        var tag_containers = $('settings_tags_content').getElementsByClassName('tag_content');
		for (var i = 0; i < tag_containers.length; i++) {
			existingTags.push(tag_containers[i].innerHTML.unescapeHTML());
		};

        return existingTags;
    },

    getNewTags: function(){
        var newTags = new Array();

		var tag_containers = this.tags_module.getElementsByTagName('input');
		for (var i = 0; i < tag_containers.length; i++) {
			newTags.push(tag_containers[i].value);
		}

        return newTags;
    },

    getTags: function(){
		var tags = new Array();
        tags = tags.concat(this.getExistingTags());
        tags = tags.concat(this.getNewTags());

        return tags;
		
	},
	
	// create tag delete buttons and set events for deletion
	handleDeleteTags: function() {
		var current_tags = this.tags_content_ul.getElementsByTagName('li');
		
		// remember tags content
        var numCurrentTags = current_tags.length;
		for (var i = 0; i < numCurrentTags; i++) {
            var currentTag = current_tags[i];
            var currentTagContent = currentTag.getElementsByClassName('tag_content')[0].innerHTML;

			// insert delete buttons into dom
			var tagDeleteButton = document.createElement('a');
			tagDeleteButton.href = 'javascript:void(0);';
			tagDeleteButton.innerHTML = '[x]';

			currentTag.appendChild(tagDeleteButton);
			
			Event.observe(tagDeleteButton,
                          'click',
                          function() {
                              //this.obj.tags_content_ul.removeChild(this.currentTag);
                              this.obj.delete_tag_callback(this.currentTagContent);
                          }.bindAsEventListener({
                                                    obj: this,
                                                    currentTag: currentTag,
                                                    currentTagContent: currentTagContent
                                                }));
		}
		
	},
	
	setEditableBy: function(editable_by){
		
		// loop through editable_by array and create input elements
		for (var i=0; i < editable_by.length; i++) {
			var new_input = document.createElement('input');
			new_input.value = editable_by[i];
			this.editable_by_fields_container.appendChild(new_input);
		}
		
	},
	
	setViewableBy: function(viewable_by){
		
		// loop through viewable_by array and create input elements
		for (var i=0; i < viewable_by.length; i++) {
			var new_input = document.createElement('input');
			new_input.value = viewable_by[i];
			this.viewable_by_fields_container.appendChild(new_input);
		}
		
	}, 
	
	getPanelHeight: function(){
		
		this.panel_height = Element.getHeight(this.settings_panel);
		return this.panel_height;
		
	}
	
	
});
