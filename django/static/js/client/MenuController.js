/**
 * @author Chris Yap
 * 	Flowgram Client Menu Controller
 */

var MenuController = Class.create();

Object.extend(MenuController.prototype, {
    lastXpos_: 0,
    lastYpos_: 0,
    visible_: false,

	initialize: function(){
		
		// init wrapper
		this.menu_div = document.createElement('div');
		Element.addClassName(this.menu_div, 'wrapper_menu_panel');
		Event.observe(this.menu_div,
                      'mouseover',
                      function() {
                          this.showMenu();
                      }.bindAsEventListener(this));
		Event.observe(this.menu_div,
                      'mouseout',
                      function() {
                          this.hideMenu();
                      }.bindAsEventListener(this));
		
		// init left side and set close event on mouseover
		this.menu_div_left = document.createElement('div');
		Element.addClassName(this.menu_div_left, 'menu_left');
		this.menu_div.appendChild(this.menu_div_left);
		
		// init ul
		this.menu_ul = document.createElement('ul');
		Element.addClassName(this.menu_ul, 'menu_panel');
		this.menu_div.appendChild(this.menu_ul);
		
		// init right side and set close event on mouseover
		this.menu_div_right = document.createElement('div');
		Element.addClassName(this.menu_div_right, 'menu_right');
		this.menu_div.appendChild(this.menu_div_right);
		
		// init bottom side and set close event on mouseover
		this.menu_div_bottom = document.createElement('div');
		Element.addClassName(this.menu_div_bottom, 'menu_bottom');
		this.menu_div.appendChild(this.menu_div_bottom);
		
		// insert menu into dom - initial display is set to none
		this.menu_div.style.display = 'none';
		document.body.appendChild(this.menu_div);
		
	},
	
    toggleMenuVisibility: function(xpos, ypos) {
        if (this.visible_) {
            this.hideMenu();
        } else {
            this.showMenu(xpos, ypos);
        }
    },
    
	showMenu: function(opt_xpos, opt_ypos) {
        var xpos = typeof(opt_xpos) == 'undefined' ? this.lastXpos_ : opt_xpos;
        var ypos = typeof(opt_ypos) == 'undefined' ? this.lastYpos_ : opt_ypos;
        this.lastXpos_ = xpos;
        this.lastYpos_ = ypos;

        if (MenuController.showingMenu_) {
            MenuController.showingMenu_.hideMenu();
        }
        MenuController.showingMenu_ = this;

        if (this.hideMenuTimeout_) {
            window.clearTimeout(this.hideMenuTimeout_);
            this.hideMenuTimeout_ = null;
        }

        this.menu_div.style.left = (xpos-20) + 'px';
		this.menu_div.style.top = ypos + 'px';
		this.menu_div.style.display = 'block';
		
		// get menu height and use it to set height of invisible left and right side divs
		var menu_height = Element.getHeight(this.menu_div);
		this.menu_div_left.style.height = (menu_height-20) + 'px';
		this.menu_div_right.style.height = (menu_height-20) + 'px';
		
        this.visible_ = true;
	},
	
	hideMenu: function() {
        MenuController.showingMenu_ = null;

        this.hideMenuTimeout_ = window.setTimeout(
            function() {
                this.menu_div.style.display = 'none';
                this.visible_ = false;
                this.hideMenuTimeout_ = null;
            }.bind(this),
            250);
	},
	
	addMenuItem: function(item_content, item_callback, item_location, opt_itemValue){
	    var my_item_callback = item_callback;
	
	    // grab all existing menu item elements
		this.existing_menu_items = this.menu_ul.getElementsByTagName('li');
		
	    item_location = item_location || this.existing_menu_items.length;
	
		// create new menu item element, set its contents, and set callback on click event
		var menu_item = document.createElement('li');
		menu_item.innerHTML = item_content;
        menu_item.value_ = opt_itemValue || null;

		Event.observe(menu_item, 'click', function() {
		    if(my_item_callback && (this.hasClassName('disabled') == false)) {
		        eval(my_item_callback);
		    }
		}.bind(menu_item));
		
		// figure out previous item
		var next_item = '';
		var next_item_number = item_location;
		if (this.existing_menu_items[next_item_number] != null) {
			next_item = this.existing_menu_items[next_item_number];
		}
		
		// insert item
		if (next_item != '') {
			this.menu_ul.insertBefore(menu_item, next_item);
		}
		else {
			this.menu_ul.appendChild(menu_item);
		}
		
		// set rollover behavior on new item
		Event.observe(menu_item, 'mouseover', function()
		{
			Element.addClassName(this, 'over');
		}
		.bindAsEventListener(menu_item));
		
		Event.observe(menu_item, 'mouseout', function()
		{
			Element.removeClassName(this, 'over');
		}
		.bindAsEventListener(menu_item));
		
	},

    //renameFirstItem: function(new_title) {
    //    var items = this.menu_ul.getElementsByTagName('li');
    //    items[0].innerHTML = new_title;
    //},

    getItemByValue: function(value) {
        var output = null;

        var items = $A(this.menu_ul.getElementsByTagName('li'));
        items.each(function(item) {
            if (item.value_ == value) {
                output = item;
            }
        });

        return output;
    },

    renameItemByValue: function(new_title, value) {
        var item = this.getItemByValue(value);
        item.innerHTML = new_title;
    },
	
    renameItem: function(new_title, position) {
        var items = this.menu_ul.getElementsByTagName('li');
        items[position].innerHTML = new_title;
    },
    
	removeMenuItem: function(item_location){
		
		// grab all existing menu item elements
		this.existing_menu_items = this.menu_ul.getElementsByTagName('li');
		
		// set item to remove
		this.remove_item = this.existing_menu_items[item_location];
		
		// remove item
		this.menu_ul.removeChild(this.remove_item);
		
	},
	
	addSeparator: function(item_location){
		
		// grab all existing menu item elements
		this.existing_menu_items = this.menu_ul.getElementsByTagName('li');
		
	    item_location = item_location || this.existing_menu_items.length;
	    
		// create new menu item element and add seperator css class
		var menu_item = document.createElement('li');
		Element.addClassName(menu_item, 'seperator');
		
		// figure out previous item
		var next_item = '';
		var next_item_number = item_location;
		if (this.existing_menu_items[next_item_number] != null) {
			next_item = this.existing_menu_items[next_item_number];
		}
		
		// insert item
		if (next_item != '') {
			this.menu_ul.insertBefore(menu_item, next_item);
		}
		else {
			this.menu_ul.appendChild(menu_item);
		}
		
	},
	
	disableItem: function(item_location){
		
		// grab all existing menu item elements
		this.existing_menu_items = this.menu_ul.getElementsByTagName('li');
		
		// set li to disable
		var disable_li = this.existing_menu_items[item_location];
		
		// disable items
		Element.addClassName(disable_li, 'disabled');
		
		
	},
	
	enableItem: function(item_location){
		
		// grab all existing menu item elements
		this.existing_menu_items = this.menu_ul.getElementsByTagName('li');
		
		// set li to enable
		var disable_li = this.existing_menu_items[item_location];
		
		// enable items
		Element.removeClassName(disable_li, 'disabled');
		
	},
	
	clearMenu: function(){
		
		var menu_items = this.menu_ul.getElementsByTagName('li');
		for (var i=menu_items.length - 1; i >= 0; i--) {
			this.menu_ul.removeChild(menu_items[i]);
		};
		
	}
});
