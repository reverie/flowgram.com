/**
 * @author Chris Yap
 * 	Flowgram Add URLs Controller
 */

var AddUrlsController = Class.create();

Object.extend(AddUrlsController.prototype, {
	initialize: function(){ 
		
		this.sidenavArray = Element.select($('add_urls_sidenav'), 'li');
		this.initSidenav();
		if (window.parent.g_FlashConnection.flex.getNamedHashVariables().presetnavstate && !window.parent.g_FlashConnection.alreadyLoadedMaker) {
			window.parent.g_FlashConnection.addUrlsNavState = window.parent.g_FlashConnection.flex.getNamedHashVariables().presetnavstate;
		}
		var navState = window.parent.g_FlashConnection.addUrlsNavState;
		var homeWidgetID = window.parent.g_FlashConnection.flex.getNamedHashVariables().homewidgetid;
		
		if (navState) {
			this.presetState(navState);
		}
		else {
			navState = 'webpages';
			if (homeWidgetID && !window.parent.g_FlashConnection.alreadyLoadedMaker) {
				/*
				this.devWidgetArray = ['8HBDOR5O2QVZQO', 'KFU62O8E5DUUFS', '1YEU10Z8HJG63E', '270', 'bloggerPromo'];
				this.betaWidgetArray = ['1ADMKAPBUZF4N2', '8HBDOR5O2QVZQO', '599AKQ6V1S6YQJ', 'EDTLPSBZVV8DB6', 'bloggerPromo'];
				this.currentWidgetArray = [];
				var currentDomain = getDomain();
				if (currentDomain.indexOf('dev') >= 0) {
					this.currentWidgetArray = this.devWidgetArray;
				}
				else if (currentDomain.indexOf('beta') >= 0) {
					this.currentWidgetArray = this.betaWidgetArray;
				}
				*/
				
				/* promo order: say what's up to a friend, make fun of something, explain something, talk about your pictures, blogger promo */
				
				this.currentWidgetArray = ['sayWhatsUpToAFriend', 'makeFunOfSomething', 'explainSomething', 'talkAboutYourPhotos', 'bloggerPromo', 'travelPlanning'];
				if (homeWidgetID == this.currentWidgetArray[0].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/create_landing_quad1.html');
				}
				else if (homeWidgetID == this.currentWidgetArray[1].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/create_landing_quad2.html');
				}
				else if (homeWidgetID == this.currentWidgetArray[2].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/create_landing_quad3.html');
				}
				else if (homeWidgetID == this.currentWidgetArray[3].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/create_landing_quad4.html');
					navState = 'photos';
				}
				else if (homeWidgetID == this.currentWidgetArray[4].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/blogger_promo.html');
				}
				else if (homeWidgetID == this.currentWidgetArray[5].toLowerCase()) {
					var dc = new DialogController('/media/dialogs/travel_planning.html');
				}
			}
			this.presetState(navState);
		}
		window.parent.g_FlashConnection.addUrlsNavState = null;
		window.parent.g_FlashConnection.alreadyLoadedMaker = true;
		
	},
	
	initSidenav: function() {
		
		// set global nav rollover events
		this.sidenavArray = Element.select($('add_urls_sidenav'), 'li');
		for (var i=0; i < this.sidenavArray.length; i++) {
			
			// set mouseover event
			Event.observe(this.sidenavArray[i], 'mouseover', function()
			{
				Element.addClassName(this.nav_item, 'over');
			}
			.bindAsEventListener({obj:this, nav_item:this.sidenavArray[i]}));
			
			// set mouseout event
			Event.observe(this.sidenavArray[i], 'mouseout', function()
			{
				Element.removeClassName(this.nav_item, 'over');
			}
			.bindAsEventListener({obj:this, nav_item:this.sidenavArray[i]}));
			
			// set click event
			Event.observe(this.sidenavArray[i], 'click', function()
			{
				Element.removeClassName(this.nav_item, 'over');
				this.handleSidenavClick(this.nav_item.id);
			}
			.bindAsEventListener({obj:this, nav_item:this.sidenavArray[i], handleSidenavClick:this.handleSidenavClick}));

		};
		
	},
	
	handleSidenavClick: function(selected_nav_item) {
		if (!($(selected_nav_item).hasClassName('on'))) {
			this.sidenavArray = Element.select($('add_urls_sidenav'), 'li');
			var old_content_item = $('add_urls_sidenav').select('li[class="on"]')[0];
			old_content_item = old_content_item.id.replace(/sidenav_/, "");
			old_content_item = 'content_' + old_content_item;
			var selected_content_item = selected_nav_item.replace(/sidenav_/, "");
			selected_content_item = 'content_' + selected_content_item;
			new Effect.Fade($(old_content_item), {duration: .2});
			setTimeout(function() { new Effect.Appear($(selected_content_item), {duration: .3, queue: 'end'}) }.bind(this), 300);
			for (var i=0; i < this.sidenavArray.length; i++) {
				Element.removeClassName(this.sidenavArray[i], 'on');
			}
			Element.addClassName($(selected_nav_item), 'on')
		}
	},
	
	presetState: function(stateID) {
		var navStateID = 'sidenav_' + stateID;
		var contentStateID = 'content_' + stateID;
		Element.addClassName($(navStateID), 'on');
		$(contentStateID).style.display = 'block';
	},
	
	handleFileUpload: function() {

		$('loading_stripes_file_uploader').style.visibility = 'visible';
		Element.removeClassName($('fileUploaderMessageArea'), 'messageArea-error');
		Element.removeClassName($('fileUploaderMessageArea'), 'messageArea-normal');
		photoUploadInitiated = true;
		$('fileUploaderForm').submit();
		
	},
	
	onFileUploadComplete: function() {

		var uploaderResponse = $('fileUploaderIFrame').contentDocument;
		if (sniff_br_id == 'msie') { // Internet Explorer
			uploaderResponse = $('fileUploaderIFrame').contentWindow.document;
		}
		
		this.success_flag = uploaderResponse.getElementById('succeeded').innerHTML;
		
		// error case
		if (this.success_flag == 0) {
			$('loading_stripes_file_uploader').style.visibility = 'hidden';
			Element.addClassName($('fileUploaderMessageArea'), 'messageArea-error');
			$('fileUploaderMessageArea').innerHTML = 'The file upload failed.  Please ensure your file is of type JPG, GIF, or PNG, and that the file size is 10MB or less.';
		}
		
		// success case
		else {
			var uploaderXMLString = uploaderResponse.getElementById('content').innerHTML.unescapeHTML();
			window.parent.g_FlashConnection.flex.addPageToFlowgram(uploaderXMLString);
			$('loading_stripes_file_uploader').style.visibility = 'hidden';
			Element.addClassName($('fileUploaderMessageArea'), 'messageArea-normal');
			$('fileUploaderMessageArea').innerHTML = 'File successfully uploaded.';
		}
		
		photoUploadInitiated = false;
	}
	
	
});
