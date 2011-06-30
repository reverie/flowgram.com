/**
 * @author Chris Yap
 * 	Flowgram Website Sharing Controller
 */

var SharingController = Class.create();

Object.extend(SharingController.prototype, {
	initialize: function(fgid, fgtitle, fgurl, isLoggedIn) {
		
		this.fgId = fgid;
		this.fgTitle = fgtitle;
		this.fgUrl = fgurl;
		this.isLoggedIn_ = isLoggedIn;
		this.token = $('csrf_token').innerHTML;
		
		// set up fg details url and widget code
		this.baseUrl = document.location.protocol + '//' + document.location.host;
		this.fgShareUrl = this.baseUrl + this.fgUrl;
		this.fgShareUrlFb = this.baseUrl + '/fgr/' + this.fgId;
		this.widgetUrl = this.baseUrl + "/widget/flexwidget.swf";
		this.fgShareWidgetCode = this.getContent(false);
		
		// permalink and widget embed
		$('fgShareLink').value = this.fgShareUrl;
		$('fgShareEmbed').value = this.fgShareWidgetCode;
		
		// fire up gigya
		this.initGigya();
		
	},
	
	getContent: function(hasLinks) {

		return ['<object type="application/x-shockwave-flash" data="', this.widgetUrl, '" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" width="400" height="342">',
	            '<param name="movie" value="', this.widgetUrl, '" />',
	            '<param name="flashVars" value="id=', this.fgId, (hasLinks ? '&hasLinks=true' : ''), '" />',
	            '<param name="allowScriptAccess" value="always" />',
	            '<param name="allowNetworking" value="all" />',
	            '<param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" />',
	        '</object>'].join('');
	},
	
	initGigya: function() {
		
		var fbParams = $H({
	        't': this.fgTitle,
	        'u': this.fgShareUrlFb + '%3Fsource=facebook'
	    }).toQueryString();
	    
		var links = '<br /><a href="' + this.fgShareUrl + '">Play this Flowgram</a>';

	    var contentandlinks = this.getContent(true) + links;

	    // Orkut just takes the embed and uses swfobject instead.
	    var orkutContent =
	            '<object><embed src="' + this.widgetUrl + '" ' + 
	            'quality="high" width="400" height="300" type="application/x-shockwave-flash" ' + 
	            'flashVars="id=' + this.fgId + '&hasLinks=true" /></object>' +
	            links;

	    // Tagged does something similar.
	    var taggedContent = orkutContent;

	    // Bebo does some strange things, including stripping out flashvars
	    var beboContent =
	            '<object type="application/x-shockwave-flash" data="' + this.widgetUrl + 
	                '?id=' + this.fgId + '&hasLinks=true' +
	                '" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" width="400" height="300">' +
	                '<param name="movie" value="' + this.widgetUrl + '?id=' + this.fgId + '&hasLinks=true' + '" />' +
	                '<param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" />' +
	            '</object>' +                    
	            links;

	    // Wordpress disallows flash movies entirely unless they're on a whitelist.
	    var wordpressContent =
	            '<a href="' + this.fgShareUrl + '">' + this.fgTitle + '</a>';

		var pconf={
			defaultContent: this.fgShareWidgetCode,
			beboContent: beboContent,
			myspaceContent: contentandlinks,
			orkutContent: orkutContent,
			taggedContent: taggedContent,
			wordpressContent: wordpressContent,
			netvibesContent: contentandlinks,
			facebookURL: 'http://www.facebook.com/sharer.php?' + fbParams, 
			UIConfig: '<config><display showDesktop="false" showEmail="false" useTransitions="true" showBookmark="true" showCodeBox="false" networksWithCodeBox="" networksToShow="facebook, myspace, blogger, wordpress, typepad, livejournal, friendster, orkut, bebo, tagged, hi5, livespaces, piczo, freewebs, blackplanet, myyearbook, vox, xanga, multiply, igoogle, netvibes, pageflakes, migente, *"></display><body><background background-color="#E1F1F5" frame-thickness="0"></background><controls corner-roundness="4;4;4;4"><snbuttons type="textUnder"></snbuttons><servicemarker gradient-color-begin="#F4F4F4" gradient-color-end="#D5D5D5"></servicemarker></controls></body></config>'
			};
		
		Wildfire.initPost('370971', 'divWildfirePost', 600, 240, pconf);
		Wildfire.onPostProfile = function() {
			// analytics tracking here
			pageTracker._trackPageview('/share/' + this.fgId + '/gigyasuccess');
			asrc.recordStat('fg_share_gigya_website', '0', this.fgId);
		};
		
	},
	
	sendShareEmail: function() {
		
		var emailFromName = $('fgShareEmailFromName');
        var emailFromEmail = $('fgShareEmailFromEmail');
        var emailTo = $('fgShareEmailTo');
        var emailMessage = $('fgShareEmailMessage');
		this.loading = $('fgShareEmailLoading');
		this.status = $('fgShareEmailStatus');
		this.status.innerHTML = '';
		Element.removeClassName(this.status, 'error');
		Element.removeClassName(this.status, 'success');

        if (!this.isLoggedIn_ && (!emailFromEmail.value || !emailFromName.value)) {
            this.status.innerHTML = 'The "from" name and email address are required since you\'re not logged in.';
			Element.addClassName(this.status, 'error');
			return false;
        }

        if(emailFromEmail.value && !isValidEmail(emailFromEmail.value)) {
            this.status.innerHTML = 'Your email address is invalid.';
			Element.addClassName(this.status, 'error');
            return false;
        }

        var emailText = emailTo.value.toLowerCase();
		emailText = emailText.replace(/ /, "");
        var emails = cleanEmails(emailText);
		emails = emails.split(",");
        for(var i = 0; i < emails.length; i++) {
            if(!isValidEmail(emails[i])) {
                this.status.innerHTML = "Your to email address list is invalid. Please enter a comma separated list of email addresses.";
				Element.addClassName(this.status, 'error');
                return false;
            }
        }

        // If the user is not logged in, check to see if they specified both a "from" name and email
        // address.
        if (!this.isLoggedIn_) {
            if (!emailFromName.value || !emailFromEmail.value) {
                this.status.innerHTML = 'Please specify your name and email address or log in.';
				Element.addClassName(this.status, 'error');
                return false;
            }
        }
        
        // Check to see if the use specified recipient email addresses.
        if (!emailTo.value) {
            this.status.innerHTML = 'Please specify at least one recipient email address.  Use commas to separate multiple addresses.';
            Element.addClassName(this.status, 'error');
			return false;
        }

		this.loading.style.visibility = 'visible';

        var params = $H({
                             'csrfmiddlewaretoken': this.token,
                             'flowgram_id': this.fgId,
                             'recipients': emailTo.value,
                             'message': emailMessage.value,
                             'from_name': emailFromName.value,
                             'from_email': emailFromEmail.value,
                             'cc_self': false,
                             'add_messages': false
                        }).toQueryString();
        
        new Ajax.Request('/api/share/', 
        {
             asynchronous: true,
             method: 'POST', 
             parameters: params,
             onComplete: this.sendEmailComplete.bind(this)
        });
		
	},
	
	sendEmailComplete: function() {
		this.status.innerHTML = 'Email sent.';
		Element.addClassName(this.status, 'success');
		this.loading.style.visibility = 'hidden';
	},
	
	sendYouTubeRequest: function(checkEmail) {
		
		this.fgShareVideoExportStep1 = $('fgShareVideoExportStep1');
		this.fgShareVideoExportStep2 = $('fgShareVideoExportStep2');
		this.fgShareVideoExportLoading = $('fgShareVideoExportLoading');
		this.fgShareVideoExportEmailLoading = $('fgShareVideoExportEmailLoading');
		var fgShareVideoExportEmail = $('fgShareVideoExportEmail').value;
		fgShareVideoExportEmail = fgShareVideoExportEmail.replace(/ /, "");
		var fgShareVideoExportOptionsPopups = $('fgShareVideoExportOptionsPopups').checked;
		this.fgShareVideoExportError = $('fgShareVideoExportError');
		this.fgShareVideoExportStatus = $('fgShareVideoExportStatus');
		this.fgShareVideoExportStatusCheck = $('fgShareVideoExportStatusCheck');
		
		if (checkEmail) {
			this.fgShareVideoExportEmailLoading.style.visibility = 'visible';
			if (!isValidEmail(fgShareVideoExportEmail)) {
				this.fgShareVideoExportError.innerHTML = 'It appears your email is invalid.';
				this.fgShareVideoExportEmailLoading.style.visibility = 'hidden';
				return false;
			}
			
			else {
				this.fgShareVideoExportEmailLoading.style.visibility = 'hidden';
				this.fgShareVideoExportError.innerHTML = '';
				new Effect.Fade(this.fgShareVideoExportStep1,{duration:.5});
				new Effect.Appear(this.fgShareVideoExportStep2,{duration:1, queue:'end'});
				return false;
			}
		}
		
		this.fgShareVideoExportLoading.style.visibility = 'visible';
		
		var ytParams = $H({
                             'csrfmiddlewaretoken': this.token,
                             'flowgram_id': this.fgId,
							 'use_highlight_popups': fgShareVideoExportOptionsPopups,
							 'request_email': fgShareVideoExportEmail
                        }).toQueryString();
		
		new Ajax.Request('/api/exporttovideo/', 
        {
	        asynchronous: true,
	        method: 'POST', 
	        parameters: ytParams,
	        onComplete: function(transport) {
				var response_json = transport.responseText.evalJSON();
				var checkUrl = this.baseUrl + '/exporttovideo/check/' + response_json.body;
				this.fgShareVideoExportStatusCheck.href = checkUrl;
				this.fgShareVideoExportStatusCheck.innerHTML = checkUrl;
				this.fgShareVideoExportLoading.style.visibility = 'hidden';
				new Effect.Fade(this.fgShareVideoExportStep2,{duration:.5});
				new Effect.Appear(this.fgShareVideoExportStatus,{duration:1, queue:'end'});
			}.bind(this)
        });
	}
	
});