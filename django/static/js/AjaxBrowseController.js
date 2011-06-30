/**
 * @author Chris Yap
 * 	Flowgram Ajax Browse Controller
 */

var AjaxBrowseController = Class.create();

Object.extend(AjaxBrowseController.prototype, {
	initialize: function(user){ 
		
		this.nav = $('nav_ajax_browse');
		this.nav_items = Element.select(this.nav, 'li');
		this.setLoadingDivSize();
		this.loading_div = $('fg_browse_content_loading');
		var user = (user == null) ? '' : user;
		this.user = user;
		
	},
	
	handleViewSwitch: function(browse_type) {
		
		this.browse_type = browse_type;
		this.setNavStates();
		this.getViewCache = this.getView.bindAsEventListener(this);
		new Effect.Appear(this.loading_div,{duration: .3});
		setTimeout(this.getViewCache.bind(this), 300);
		
	},
	
	setNavStates: function() {
		
		this.old_selected = Element.select(this.nav, 'li[class="selected"]')[0];
		this.new_selected = 'nav_ajax_browse_' + this.browse_type;
		Element.removeClassName(this.old_selected, 'selected');
		Element.addClassName($(this.new_selected), 'selected');
		
		this.browse_more_link = '/browse/' + this.browse_type.replace(/_/, "");
		if (this.user == '') {
			$('fg_browse_content_more_link').href = this.browse_more_link;
		}
		
	},
	
	getView: function() {
		
		this.path = '/browse/ajax/' + this.browse_type;
		if (this.user != '') {
			this.path += '/' + this.user;
		}
		new Ajax.Updater($('fg_browse_content'), this.path, 
		{
			method: 'GET',
			onComplete: function()
			{
				
				new Effect.Fade($('fg_browse_content_loading'),{duration:.5});
			
			}.bind(this)
		});
		
	},
	
	setLoadingDivSize: function() {
		
		$('fg_browse_content_loading').style.width = $('fg_browse_content').getWidth() + 'px';
		$('fg_browse_content_loading').style.height = $('fg_browse_content').getHeight() + 'px';
		
	}
	
	
});
