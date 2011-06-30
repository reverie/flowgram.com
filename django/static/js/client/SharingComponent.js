/**
 * @author Brian Westphal / Chris Yap / Mr. Bigglesworth
 * Sharing Component
 */

var SharingComponent = Class.create();

Object.extend(SharingComponent.prototype, Component.prototype);
SharingComponent.superclass = Component;
SharingComponent.$super = Component.prototype;

/**
 * The SharingComponent represents a reusable UI controller class for the sharing component.  This
 * type of component is used both in the website and in the toolbar.  Different options are shown,
 * depending on whether or not the user is the owner of the FlowGram to be shared.
 */
Object.extend(SharingComponent.prototype, {
    /**
     * Initializes the controller.
     */
    initialize: function(inPanel, opt_flowgramId, opt_isOwner, opt_isLoggedIn, opt_ownerName,
                             opt_ownerUrl, opt_title, opt_description, opt_isPublic) {
        SharingComponent.$super.initialize.call(this);
        
        /**
         * Denotes whether or not the layout should be for a panel or the website.
         * @type boolean
         * @private
         */
        this.inPanel_ = inPanel;

        this.setFlowgramData(opt_flowgramId, opt_isOwner, opt_isLoggedIn, opt_ownerName,
                             opt_ownerUrl, opt_title, opt_description, opt_isPublic);
    },

    // PRIVATE FIELDS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_SharingComponent',

    /**
     * The ID used to identify the widget uniquely.
     * @private
     * @type Number
     */
    id_: -1,

    /**
     * Denotes whether or not the toolbar (if applicable) is in tutorial mode.  If it is, public
     * sharing is disabled, and the user's email address is used.
     * @private
     * @type Boolean
     */
    inTutorialMode_: false,

    /**
     * The last on continue clicked handler.
     * @private
     * @type Function
     */
    lastOnContinueClicked_: null,

    shouldResetEmailMessage_: true,

    /**
     * The email address of the current user.  This is only valid when in tutorial mode.
     * @private
     * @type String
     */
    userEmailAddress_: null,

    // PUBLIC METHODS-------------------------------------------------------------------------------
    
    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.id_ = SharingComponent.allocateId_();
        this.domElement_ = Component.newElementFromString(
            SharingComponent.getHtmlString(this.inPanel_),
            {
                prefix: this.cssPrefix_,
                id: this.id_
            });
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        // Setting up tab event handlers.
        var emailTab = this.getSubElement('emailTab');
        emailTab.observe('click', this.onEmailTabClicked_.bindAsEventListener(this));
        var socialNetworkTab = this.getSubElement('socialNetworkTab');
        socialNetworkTab.observe('click', this.onSocialNetworkTabClicked_.bindAsEventListener(this));
        var imTab = this.getSubElement('imTab');
        imTab.observe('click', this.onImTabClicked_.bindAsEventListener(this));

        // Setting up the event listeners for the privacy control.
        var privacyControlPublic = this.getSubElement('privacyControlPublic');
        Event.observe(privacyControlPublic,
                      'click',
                      this.onPrivacyControlClicked_.bindAsEventListener(this));
        var privacyControlUnlisted = this.getSubElement('privacyControlUnlisted');
        Event.observe(privacyControlUnlisted,
                      'click',
                      this.onPrivacyControlClicked_.bindAsEventListener(this));

        // Setting up the event listeners for the edit and save buttons.
        var editButton = this.getSubElement('editButton');
        Event.observe(editButton, 'click', this.onEditButtonClicked_.bindAsEventListener(this));
        var saveButton = this.getSubElement('saveButton');
        Event.observe(saveButton, 'click', this.onSaveButtonClicked_.bindAsEventListener(this));

        // Setting up the event listener for the email send button.
        var emailSendButton = this.getSubElement('emailSendButton');
        Event.observe(emailSendButton, 'click', this.onSendEmailClicked_.bindAsEventListener(this));
        
        // handle auto email message sig
        this.emailFromName = this.getSubElement('emailFromName');
        this.emailMessage = this.getSubElement('emailMessage');
        this.defaultEmailMessage_ = 'Hey,\n\nCheck this out.\n\n-';
        this.updateDefaultSigCache = this.updateDefaultSig.bindAsEventListener(this);
        this.handleAutoSigEventsOn();
        Event.observe(this.emailMessage, 'keypress', this.handleAutoSigEventsOff.bind(this));
        
        this.updateUi_();

        // Showing the email form to start with.
        this.onEmailTabClicked_();

        //this.makeCurvy_();

        this.setTabRolloverEvents();

        SharingComponent.$super.enterDom.call(this);
    },
    
    handleAutoSigEventsOn: function() {
        Event.observe(this.emailFromName, 'keyup', this.updateDefaultSigCache);
    },
    
    handleAutoSigEventsOff: function() {
        Event.stopObserving(this.emailFromName, 'keyup', this.updateDefaultSigCache);
    },
    
    setTabRolloverEvents: function() {
        this.pref_items = $('fg_SharingComponent-sharingControlsBox').select('div[selector="tab"]');
        
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
    },
    
    getDescription: function() {
        return this.description_;
    },

    getTitle: function() {
        return this.title_;
    },
    
    isPublic: function() {
        return this.isPublic_;
    },
    
    setFlowgramData: function(flowgramId, isOwner, isLoggedIn, ownerName, ownerUrl, title,
                              description, isPublic) {
        this.flowgramId_ = flowgramId;
        this.isOwner_ = isOwner;
        this.isLoggedIn_ = isLoggedIn;
        //this.ownerName_ = ownerName ? ownerName.escapeHTML() : ownerName;
        this.ownerName_ = ownerName;
        this.ownerUrl_ = ownerUrl;
        //this.title_ = title ? title.escapeHTML() : title;
        this.title_ = title;
        //this.description_ = description ? description.escapeHTML() : description;
        this.description_ = description;
        this.isPublic_ = isPublic;

        if (this.isInDom()) {
            this.updateUi_();
        }

        this.shouldResetEmailMessage_ = true;
    },
    
    setInTutorialMode: function(inTutorialMode, opt_userEmailAddress) {
        this.inTutorialMode_ = inTutorialMode;
        this.userEmailAddress_ = opt_userEmailAddress || null;
        
        if (this.isInDom()) {
            this.updateUi_();
        }
    },
    
    // PRIVATE METHODS------------------------------------------------------------------------------
    
    changePrivacy_: function(isPublic) {
        this.isPublic_ = isPublic;
        this.updatePrivacyControl_();
        this.updatePrivacyDescription_();

        var tokenDiv = $('csrf_token');

        var params = $H({
                             'csrfmiddlewaretoken': tokenDiv ?
                                 tokenDiv.innerHTML :
                                 window.parent.g_FlashConnection.flex.getToken(),
                             'flowgram_id': this.flowgramId_,
                             'public': isPublic
                        }).toQueryString();
        
        new Ajax.Request('/api/changeprivacy/', 
                         {
                              asynchronous: true,
                              method: 'POST', 
                              parameters: params
                         });

        this.shouldResetEmailMessage_ = false;
        this.dispatchEvent('flowgramChanged');
    },

    getPlayUrl_: function(widget) {
        return [
            document.location.protocol,
            '//',
            document.location.host,
            widget ? '/wp/' : '/p/',
            this.flowgramId_].join ('');
    },
    
    getWidgetUrl_: function() {
        return document.location.protocol + '//' + document.location.host + "/widget/flexwidget.swf";
    },

    isValidEmail_: function(email) {
        var regex = new RegExp("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?");
        return regex.test(email);
    },

    makeCurvy_: function() {
        settings = {
          tl: { radius: 5 },
          tr: { radius: 5 },
          bl: { radius: 5 },
          br: { radius: 5 },
          antiAlias: true,
          autoPad: false
        }

        var cornersObj = new curvyCorners(settings, "curved");
        cornersObj.applyCornersToAll();
    },

    onEditButtonClicked_: function() {
        var editButton = this.getSubElement('editButton');
        editButton.style.display = 'none';

        var saveButton = this.getSubElement('saveButton');
        saveButton.style.display = 'block';

        var title = this.getSubElement('title');
        title.style.display = 'none';

        var titleEditor = this.getSubElement('titleEditor');
        titleEditor.value = this.title_;
        titleEditor.style.display = 'inline';

        var description = this.getSubElement('description');
        description.style.display = 'none';

        var descriptionEditor = this.getSubElement('descriptionEditor');
        descriptionEditor.value = this.description_;
        descriptionEditor.style.display = 'inline';
    },
        
    onEmailTabClicked_: function() {
        this.closeAllTabs_();
        this.showTab_('email');
    },
    
    onShare_: function(evt) {
        pageTracker._trackPageview('/toolbar/panels/share/success/socialnetwork');
    },

    onSocialNetworkTabClicked_: function() {
        this.closeAllTabs_();
        this.showTab_('socialNetwork');

        var fbParams = $H({
            't': this.title_,
            'u': this.getPlayUrl_(true) + '%3Fsource=facebook' // Using %3F to represent ?
        }).toQueryString();

        var content = function(hasLinks) {
            return [
                '<object type="application/x-shockwave-flash" data="', this.getWidgetUrl_(), '" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" width="400" height="300">',
                    '<param name="movie" value="', this.getWidgetUrl_(), '" />',
                    '<param name="flashVars" value="id=', this.flowgramId_, (hasLinks ? '&hasLinks=true' : ''), '" />',
                    '<param name="allowScriptAccess" value="always" />',
                    '<param name="allowNetworking" value="all" />',
                    '<param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" />',
                '</object>'].join('');
        }.bind(this);

        var links = '<br /><a href="' + this.getPlayUrl_(true) + '">Play this Flowgram</a>';
        
        var contentandlinks = content(true) + links;
        
        // Orkut just takes the embed and uses swfobject instead.
        var orkutContent =
                '<object><embed src="' + this.getWidgetUrl_() + '" ' + 
                'quality="high" width="400" height="300" type="application/x-shockwave-flash" ' + 
                'flashVars="id=' + this.flowgramId_ + '&hasLinks=true" /></object>' +
                links;
        
        // Tagged does something similar.
        var taggedContent = orkutContent;

        // Bebo does some strange things, including stripping out flashvars
        var beboContent =
                '<object type="application/x-shockwave-flash" data="' + this.getWidgetUrl_() + 
                    '?id=' + this.flowgramId_ + '&hasLinks=true' +
                    '" codebase="http://download.macromedia.com/pub/shockwave/cabs/flash/swflash.cab" width="400" height="300">' +
                    '<param name="movie" value="' + this.getWidgetUrl_() + '?id=' + this.flowgramId_ + '&hasLinks=true' + '" />' +
                    '<param name="pluginurl" value="http://www.adobe.com/go/getflashplayer" />' +
                '</object>' +                    
                links;

        // Wordpress disallows flash movies entirely unless they're on a whitelist.
        var wordpressContent =
                '<a href="' + this.getPlayUrl_(true) + '">' + this.title_ + '</a>';
        
        var pconf = {
            defaultContent: content(false),
            beboContent: beboContent,
            myspaceContent: contentandlinks,
            orkutContent: orkutContent,
            taggedContent: taggedContent,
            wordpressContent: wordpressContent,
            netvibesContent: contentandlinks,
            facebookURL: 'http://www.facebook.com/sharer.php?' + fbParams,
            UIConfig: '<config><display showEmail="false" showBookmark="false" networksToHide="hi5, livespaces" /><body font="Arial"><background corner-roundness="4" background-color="#FFFFFF" /></body></config>'
        };
        
        Wildfire.onPostProfile = this.onShare_;
        
        Wildfire.initPost('157581', 'gigyaForm', 385, 250, pconf);
//        this.showInstructions_(
//            'socialNetwork',
//            'Clicking "continue" will open a new window and prompt you to login to your Facebook account.',
//            this.onSocialNetworkTabContinueClicked_.bindAsEventListener(this));
    },

    onSocialNetworkTabContinueClicked_: function() {
        if (this.getSubElement('instructionsMakePublic').checked) {
            this.changePrivacy_(true);
        }

        var params = $H({
                             'u': this.getPlayUrl_(true),
                             't': this.title_
                        }).toQueryString();
        
        
        window.open('http://www.facebook.com/sharer.php?' + params,
                    'sharer',
                    'toolbar=0,status=0,width=626,height=436');

        pageTracker._trackPageview('/toolbar/panels/share/success/socialnetwork');
    },

    onImTabClicked_: function() {
        this.closeAllTabs_();
        this.showInstructions_(
            'im',
            'To share via chat or instant message, copy the URL, which will appear after pressing "continue", and paste it as a message to your friends!',
            this.onImTabContinueClicked_.bindAsEventListener(this));
    },

    onImTabContinueClicked_: function() {
        if (this.getSubElement('instructionsMakePublic').checked) {
            this.changePrivacy_(true);
        }

        var instructionsPage = this.getSubElement('instructionsPage');
        instructionsPage.style.display = 'none';

        var urlPage = this.getSubElement('urlPage');
        urlPage.style.display = 'block';

        var linkPage = this.getSubElement('linkPage');
        linkPage.style.display = 'none';

        var url = this.getSubElement('url');
        url.value = this.getPlayUrl_(false);
        url.select();

        pageTracker._trackPageview('/toolbar/panels/share/success/im');
    },

    onLinkTabClicked_: function() {
        this.closeAllTabs_();
        this.showInstructions_(
            'link',
            'To include the link to your FlowGram on a webpage, copy the URL that appears after pressing "continue"',
            this.onLinkTabContinueClicked_.bindAsEventListener(this));
    },

    onLinkTabContinueClicked_: function() {
        if (this.getSubElement('instructionsMakePublic').checked) {
            this.changePrivacy_(true);
        }

        var instructionsPage = this.getSubElement('instructionsPage');
        instructionsPage.style.display = 'none';

        var urlPage = this.getSubElement('urlPage');
        urlPage.style.display = 'none';

        var linkPage = this.getSubElement('linkPage');
        linkPage.style.display = 'block';

        var link = this.getSubElement('link');
        link.value = '<a href="' + this.getPlayUrl_(false) + '">' + this.title_ + '</a>';
        link.select();

        pageTracker._trackPageview('/toolbar/panels/share/success/link');
    },

    onPrivacyControlClicked_: function() {
        var privacyControlPublic = this.getSubElement('privacyControlPublic');
        var privacyControlUnlisted = this.getSubElement('privacyControlUnlisted');

        this.changePrivacy_(privacyControlPublic.checked);
    },
    
    onSaveButtonClicked_: function() {
        var titleEditor = this.getSubElement('titleEditor');
        titleEditor.style.display = 'none';

        var descriptionEditor = this.getSubElement('descriptionEditor');
        descriptionEditor.style.display = 'none';

        //this.title_ = titleEditor.value.escapeHTML();
        //this.description_ = descriptionEditor.value.escapeHTML();
        this.title_ = titleEditor.value;
        this.description_ = descriptionEditor.value;

        var editButton = this.getSubElement('editButton');
        editButton.style.display = 'block';

        var saveButton = this.getSubElement('saveButton');
        saveButton.style.display = 'none';

        var title = this.getSubElement('title');
        title.style.display = 'block';
        this.updateTitle_();

        var description = this.getSubElement('description');
        description.style.display = 'block';
        this.updateDescription_();

        this.saveTitle_();
        this.saveDescription_();
        
        this.dispatchEvent('flowgramChanged');
    },
    
    onSendEmailClicked_: function() {
        var emailFromName = this.getSubElement('emailFromName');
        var emailFromEmail = this.getSubElement('emailFromEmail');
        var emailTo = this.getSubElement('emailTo');
        var emailMessage = this.getSubElement('emailMessage');

        if (!this.isLoggedIn_ && (!emailFromEmail.value || !emailFromName.value)) {
            window.alert('The "from" name and email address are required since you\'re not logged in.');
        }

        if(emailFromEmail.value && !this.isValidEmail_(emailFromEmail.value)) {
            alert("Your email address is invalid.");
            return;
        }

        var emailText = emailTo.value.toLowerCase();
        var emails = emailText.split(",");
        for(var i = 0; i < emails.length; i++) {
            if(!this.isValidEmail_(emails[i])) {
                alert("Your to email address list is invalid. Please enter a comma separated list of email addresses.");
                return;
            }
        }

        var emailSentMessage = this.getSubElement('emailSentMessage');
        emailSentMessage.style.display = 'none';

        this.clearMessage();

        // If the user is not logged in, check to see if they specified both a "from" name and email
        // address.
        if (!this.isLoggedIn_) {
            if (!emailFromName.value || !emailFromEmail.value) {
                this.createMessage('Please specify your name and email address or log in.', 'error');
                return;
            }
        }
        
        // Check to see if the use specified recipient email addresses.
        if (!emailTo.value) {
            this.createMessage('Please specify at least one recipient email address.  Use commas to separate multiple addresses.', 'error');
            return;
        }

        var tokenDiv = $('csrf_token');

        var params = $H({
                             'csrfmiddlewaretoken': tokenDiv ?
                                 tokenDiv.innerHTML :
                                 window.parent.g_FlashConnection.flex.getToken(),
                             'flowgram_id': this.flowgramId_,
                             'recipients': emailTo.value,
                             'message': emailMessage.value,
                             'from_name': emailFromName.value,
                             'from_email': emailFromEmail.value,
                             'cc_self': false,
                             'add_messages': false
                        }).toQueryString();
        
        var emailFormLoading = this.getSubElement('emailFormLoading');
        emailFormLoading.style.display = 'block';
        var contents = this.getSubElement('contents');
        emailFormLoading.style.width = (contents.offsetWidth - 2) + 'px';
        emailFormLoading.style.height = (contents.offsetHeight - 2) + 'px';
        
        new Ajax.Request('/api/share/', 
                         {
                              asynchronous: true,
                              method: 'POST', 
                              parameters: params,
                              onComplete: this.onSendEmailComplete_.bind(this)
                         });
    },
    
    onSendEmailComplete_: function(transport) {
        // If the make public checkbox is checked, do that.
        if (this.getSubElement('emailMakePublic').checked) {
            this.changePrivacy_(true);
        }

        var emailFormLoading = this.getSubElement('emailFormLoading');
        emailFormLoading.style.display = 'none';

        var emailSentMessage = this.getSubElement('emailSentMessage');
        emailSentMessage.style.display = 'block';

        this.dispatchEvent('flowgramShared');

        pageTracker._trackPageview('/toolbar/panels/share/success/email');
    },
    
    saveDescription_: function() {
        var tokenDiv = $('csrf_token');

        // Saving the description.
        var params = $H({
                             'csrfmiddlewaretoken': tokenDiv ?
                                 tokenDiv.innerHTML :
                                 window.parent.g_FlashConnection.flex.getToken(),
                             'desc': this.description_
                        }).toQueryString();
        
        new Ajax.Request('/api/setfgdesc/' + this.flowgramId_ + '/', 
                         {
                              asynchronous: true,
                              method: 'POST', 
                              parameters: params
                         });
    },
    
    saveTitle_: function() {
        var tokenDiv = $('csrf_token');

        // Saving the title.
        var params = $H({
                             'csrfmiddlewaretoken': tokenDiv ?
                                 tokenDiv.innerHTML :
                                 window.parent.g_FlashConnection.flex.getToken(),
                             'title': this.title_
                        }).toQueryString();
        
        new Ajax.Request('/api/setfgtitle/' + this.flowgramId_ + '/', 
                         {
                              asynchronous: true,
                              method: 'POST', 
                              parameters: params
                         });
    },
    
    showInstructions_: function(tabName, instructions, onContinueClicked) {
        this.showTab_(tabName);

        var instructionsPage = this.getSubElement('instructionsPage');
        instructionsPage.style.display = 'block';

        var urlPage = this.getSubElement('urlPage');
        urlPage.style.display = 'none';

        var linkPage = this.getSubElement('linkPage');
        linkPage.style.display = 'none';
        
        var instructionsDom = this.getSubElement('instructions');
        instructionsDom.innerHTML = instructions

        var continueButton = this.getSubElement('continueButton');
        if (this.lastOnContinueClicked_) {
            continueButton.stopObserving('click', this.lastOnContinueClicked_);
        }

        continueButton.observe('click', onContinueClicked);
        this.lastOnContinueClicked_ = onContinueClicked;
    },

    closeAllTabs_: function() {
        var tabNames = ['email', 'socialNetwork', 'im'];
        tabNames.each(function(tabName) {
            var tab = this.getSubElement(tabName + 'Tab');
            tab.removeClassName(this.getCssPrefix('selectedTab'));

            var form = this.getSubElement(tabName + 'Form');
            //form.style.display = 'none';
            new Effect.Fade(form, {duration: .2});
        }.bind(this));

        var emailSentMessage = this.getSubElement('emailSentMessage');
        emailSentMessage.style.display = 'none';
    },
    
    showTab_: function(tabName) {
    
        var tab = this.getSubElement(tabName + 'Tab');
        tab.addClassName(this.getCssPrefix('selectedTab'));

        var form = this.getSubElement(tabName + 'Form');
        //form.style.display = 'block';
        setTimeout(function() { new Effect.Appear(form, {duration: .3, queue: 'end'}) }.bind(this), 300);
        
        
    },
    
    updateDescription_: function() {
        var description = this.getSubElement('description');
        description.innerHTML = this.description_ || 'No description';
        description.style.color = this.description_ ? '#000' : '#CCC';
    },
    
    updatePrivacyControl_: function() {
        var privacyControlPublic = this.getSubElement('privacyControlPublic');
        var privacyControlUnlisted = this.getSubElement('privacyControlUnlisted');

        if (!privacyControlPublic.checked && this.isPublic_) {
            privacyControlPublic.checked = true;
        } else if (!privacyControlUnlisted.checked && !this.isPublic_) {
            privacyControlUnlisted.checked = true;
        }
    },
    
    updatePrivacyDescription_: function() {
        var privacyDescription = this.getSubElement('privacyDescription');

        privacyDescription.innerHTML = this.isPublic_ ?
            SharingComponent.PrivacyDescription_.PUBLIC :
            SharingComponent.PrivacyDescription_.PRIVATE;
    },
    
    updateTitle_: function() {
        var title = this.getSubElement('title');
        title.innerHTML = this.title_ || 'Untitled';
    },
    
    updateUi_: function() {
        this.updateTitle_();
        this.updateDescription_();

        var altPrivacyControlsArea = this.getSubElement('altPrivacyControlsArea');
        if (altPrivacyControlsArea) {
            altPrivacyControlsArea.style.display = 'block';
        }
        
        this.domElement_.style.width = '990px';

        if (this.isOwner_) {
            // If the owner.

            // Hiding the owner info area.
            var ownerInfoArea = this.getSubElement('ownerInfoArea');
            ownerInfoArea.style.display = 'none';

            // Showing the edit button area.
            var editButtonArea = this.getSubElement('editButtonArea');
            editButtonArea.style.display = 'block';

            // Showing the privacy controls area.
            var privacyControlsArea = this.getSubElement('privacyControlsArea');
            privacyControlsArea.style.display = 'block';

            // Showing the "make public" areas.

            var emailMakePublicArea = this.getSubElement('emailMakePublicArea');
            emailMakePublicArea.style.display = 'block';
            var emailMakePublic = this.getSubElement('emailMakePublic');
            emailMakePublic.checked = true;

            var instructionsMakePublicArea = this.getSubElement('instructionsMakePublicArea');
            instructionsMakePublicArea.style.display = 'block';
            var instructionsMakePublic = this.getSubElement('instructionsMakePublic');
            instructionsMakePublic.checked = true;

            if (this.shouldResetEmailMessage_) {
                this.emailMessage.value = this.defaultEmailMessage_ + this.ownerName_;
            }
        } 

        else {
            // If not the owner.

            if (this.inPanel_) {
                if (altPrivacyControlsArea) {
                    altPrivacyControlsArea.style.display = 'none';
                }
                
                this.domElement_.style.width = '725px';
            }

            // Showing the owner info area.
            var ownerInfoArea = this.getSubElement('ownerInfoArea');
            ownerInfoArea.style.display = 'block';

            // Hiding the edit button area.
            var editButtonArea = this.getSubElement('editButtonArea');
            editButtonArea.style.display = 'none';

            // Hiding the privacy controls area.
            var privacyControlsArea = this.getSubElement('privacyControlsArea');
            privacyControlsArea.style.display = 'none';

            // Hiding the "make public" areas.

            var emailMakePublicArea = this.getSubElement('emailMakePublicArea');
            emailMakePublicArea.style.display = 'none';
            var emailMakePublic = this.getSubElement('emailMakePublic');
            emailMakePublic.checked = false;

            var instructionsMakePublicArea = this.getSubElement('instructionsMakePublicArea');
            instructionsMakePublicArea.style.display = 'none';
            var instructionsMakePublic = this.getSubElement('instructionsMakePublic');
            instructionsMakePublic.checked = false;

            // Updating the owner name.
            var ownerName = this.getSubElement('ownerName');
            ownerName.innerHTML = '<a href="' + this.ownerUrl_ + '">' + this.ownerName_ + '</a>';

            if (!window.parent.g_FlashConnection && (!window.current_user || window.current_user == '')) {
                window.current_user = this.emailFromName.value;
            }
            
            if (this.shouldResetEmailMessage_) {
                this.emailMessage.value = this.defaultEmailMessage_ + 
                    (window.parent.g_FlashConnection ?
                            window.parent.g_FlashConnection.flex.getUsername() :
                            window.current_user);
            }
        }

        var notLoggedInMessage = this.getSubElement('notLoggedInMessage');
        var emailFromNameLabel = this.getSubElement('emailFromNameLabel');
        var emailFromName = this.getSubElement('emailFromName');
        var emailFromEmailLabel = this.getSubElement('emailFromEmailLabel');
        var emailFromEmailInputArea = this.getSubElement('emailFromEmailInputArea');

        var loggedInDisplayStyle = this.isLoggedIn_ ? 'none' : 'block';

        notLoggedInMessage.style.display = loggedInDisplayStyle;
        emailFromNameLabel.style.display = loggedInDisplayStyle;
        emailFromName.style.display = loggedInDisplayStyle;
        emailFromEmailLabel.style.display = loggedInDisplayStyle;
        emailFromEmailInputArea.style.display = loggedInDisplayStyle;
        
        this.updatePrivacyControl_();
        this.updatePrivacyDescription_();

        /*try {
            if (this.flowgramId_) {
                swfobject.embedSWF("/widget/flexwidget.swf", 
                                   this.getCssPrefix('widget-' + this.id_),
                                   "260",
                                   "160",
                                   "9.0.28",
                                   "/flex/playerProductInstall.swf",
                                   { fgid: this.flowgramId_ }, 
                                   { wmode : "opaque" },
                                   { id: "fwidget_" + this.id_ });
            } else {
                this.getSubElement('widget').innerHTML = '';
            }
        } catch (e) { }*/

        // Updating the permalink.
        var permaLink = this.getSubElement('permaLink');
        permaLink.innerHTML = this.getPlayUrl_(false);

        // If in tutorial mode, disabling the "make public" options and setting the default email
        // address.
        if (this.inTutorialMode_) {
            var emailMakePublic = this.getSubElement('emailMakePublic');
            emailMakePublic.disabled = true;
            var emailMakePublicArea = this.getSubElement('emailMakePublicArea');
            emailMakePublicArea.style.color = '#CCC';

            var instructionsMakePublic = this.getSubElement('instructionsMakePublic');
            instructionsMakePublic.disabled = true;
            var instructionsMakePublicArea = this.getSubElement('instructionsMakePublicArea');
            instructionsMakePublicArea.style.color = '#CCC';
            
            var emailTo = this.getSubElement('emailTo');
            emailTo.value = this.userEmailAddress_;
        }
    },

    updateDefaultSig: function() {
        this.emailMessage.value = this.defaultEmailMessage_ + this.emailFromName.value;
    },

    clearMessage: function() {
        if (this.messageContainer_) {
            this.messageContainer_.parentNode.removeChild(this.messageContainer_);
            this.messageContainer_ = null;
        }        
    },

    createMessage: function(message, style_class) {
        this.clearMessage();
        this.messageContainer_ = document.createElement('p');
        this.messageContainer_.addClassName(style_class);
        this.messageContainer_.innerHTML = message;
        this.getSubElement('sharingContents').insert({ top: this.messageContainer_ });
        new Effect.Highlight(this.messageContainer_, { duration: 5 });
    }
});

// PRIVATE STATIC FIELDS----------------------------------------------------------------------------

/**
 * The ID counter.
 * @private
 * @type Number
 */
SharingComponent.ID_ = 0;

/**
 * The descriptions for different privacy settings.
 * @private
 * @enum {String}
 */
SharingComponent.PrivacyDescription_ = {
    PRIVATE: 'This FlowGram is not available directly from our website.  You can still share it manually.',
    PUBLIC: 'This FlowGram is available directly from our website.'
}

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @param {boolean} inPanel If true, layout is for panel (wider).  If false, layout is for website
 *     (more narrow).
 * @return {string} The HTML string for the component.
 */
SharingComponent.getHtmlString = function(inPanel) {
    var privacyControls = [
        '<div class="{$prefix}-privacyControlsArea">',
            '<div class="fg_panelTitle">Privacy Status</div>',
            '<div class="{$prefix}-privacyControl">',
                '<table>',
                    '<tr>',
                        '<td valign="top"><input class="{$prefix}-privacyControlPublic" type="radio" name="privacyControl-${id}" value="public"></td>',
                        '<td valign="top">&nbsp;Public&nbsp;-&nbsp;</td>',
                        '<td valign="top">For FlowGrams you want to show publicly.</td>',
                    '</tr>',
                    '<tr>',
                        '<td valign="top"><input class="{$prefix}-privacyControlUnlisted" type="radio" name="privacyControl-${id}" value="private"></td>',
                        '<td valign="top">&nbsp;Unlisted&nbsp;-&nbsp;</td>',
                        '<td valign="top">For FlowGrams you only want to share with select people.</td>',
                    '</tr>',
                '</table>',
            '</div>',
            '<div class="{$prefix}-privacyDescription"></div>',
        '</div>'
    ].join('');

    return [
        '<div class="{$prefix}">',
            '<script type="text/javascript" src="http://www.plaxo.com/css/m/js/util.js"></script>',
            '<script type="text/javascript" src="http://www.plaxo.com/css/m/js/basic.js"></script>',
            '<script type="text/javascript" src="http://www.plaxo.com/css/m/js/abc_launcher.js"></script>',
            '<script type="text/javascript">function onABCommComplete() { }</script>',
            '<table width="100%"><tr><td><div class="{$prefix}-widgetAndPrivacyControls">',
                '<div class="{$prefix}-widgetArea">',
                    //'<div id="{$prefix}-widget-{$id}" class="{$prefix}-widget"></div>',
                    '<div class="fg_panelTitle">FlowGram Details</div>',
                    '<div class="{$prefix}-title"></div>',
                    '<input class="{$prefix}-titleEditor" type="text" />',
                    '<div class="{$prefix}-description"></div>',
                    '<input class="{$prefix}-descriptionEditor" type="text" />',
                    '<div class="{$prefix}-editButtonArea">',
                        '<div class="{$prefix}-editButton"></div>',
                        '<div class="{$prefix}-saveButton"></div>',
                    '</div>',
                '</div>',
                '<table><tr><td><div class="{$prefix}-ownerInfoArea">',
                    '<div class="{$prefix}-ownerNameLabel">Created By</div>',
                    '<div class="{$prefix}-ownerName"></div>',
                '</div></td></tr></table>',
                '<div class="fg_panelTitle" style="margin-top: 20px;">Link</div>',
                '<div class="{$prefix}-permaLink"></div>',
                (!inPanel ? privacyControls : ''),
            '</div>',
            '<div class="{$prefix}-sharingControls">',
                '<div id="{$prefix}-sharingControlsBox" class="{$prefix}-sharingControlsBox">',
                    '<table class="{$prefix}-sharingTabs"><tr>',
                        '<td class="{$prefix}-emailTab" selector="tab" valign="top">Email Link:',
                            '<div class="fg_contents">',
                                '<div class="fg_highlightBg1"><div class="fg_highlightBg2"><div class="fg_highlightBg3"><div class="fg_highlightBg4"><div class="fg_highlightBg5"><div class="fg_highlightBg6">',
                                '<table><tr>',
                                    '<td><img src="/media/images/icons/email.gif"></td><td>&nbsp;Email</td>',
                                '</tr></table>',
                                '</div></div></div></div></div></div>',
                            '</div>',
                        '</td>',
                        '<td class="{$prefix}-socialNetworkTab" selector="tab" valign="top">Post FlowGram Widget:',
                            '<div class="fg_contents">',
                                '<div class="fg_highlightBg1"><div class="fg_highlightBg2"><div class="fg_highlightBg3"><div class="fg_highlightBg4"><div class="fg_highlightBg5"><div class="fg_highlightBg6">',
                                '<table>',
                                    '<tr>',
                                        '<td><img src="/media/images/icons/facebook_small.gif"></td><td class="fg_firstColumn">FaceBook</td>',
                                        '<td><img src="/media/images/icons/blogger_small.gif"></td><td>Blogger</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td><img src="/media/images/icons/myspace_small.gif"></td><td class="fg_firstColumn">MySpace</td>',
                                        '<td><img src="/media/images/icons/livejournal_small.gif"></td><td>LiveJournal</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td></td>',
                                        '<td colspan="3">Other social networks &amp; blogs</td>',
                                    '</tr>',
                                '</table>',
                                '</div></div></div></div></div></div>',
                            '</div>',
                        '</td>',
                        '<td class="{$prefix}-imTab" selector="tab" valign="top">IM Link:',
                            '<div class="fg_contents">',
                                '<div class="fg_highlightBg1"><div class="fg_highlightBg2"><div class="fg_highlightBg3"><div class="fg_highlightBg4"><div class="fg_highlightBg5"><div class="fg_highlightBg6">',
                                '<table>',
                                    '<tr>',
                                        '<td><img src="/media/images/icons/yim_small.gif"></td><td>Yahoo IM</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td><img src="/media/images/icons/aim_small.gif"></td><td>AOL IM</td>',
                                    '</tr>',
                                '</table>',
                                '</div></div></div></div></div></div>',
                            '</div>',
                        '</td>',
                    '</tr></table>',
                    '<div class="{$prefix}-contents curved">',
                        '<div class="{$prefix}-emailFormLoading"></div>',
                        '<div id="{$prefix}-sharingContents" class="{$prefix}-sharingContents">',
                            '<div class="{$prefix}-socialNetworkForm {$prefix}-socialForm" id="gigyaForm" style="display: none;"></div>',
                            '<div class="{$prefix}-emailForm" style="display: none;">',
                                '<table class="{$prefix}-emailFormTable">',
                                    '<tr>',
                                        '<td colspan="2">',
                                            '<div class="{$prefix}-emailSentMessage">Email sent successfully</div>',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td colspan="2">',
                                            '<div class="{$prefix}-notLoggedInMessage">',
                                            // TODO(westphal): Add something so that the user doesn't
                                            //                 lose their place when logging in.
                                                'You are not currently logged in.  <a href="/login/">Log in</a>',
                                            '</div>',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td><div class="{$prefix}-emailFromNameLabel">',
                                            'Your Name:',
                                        '</div></td>',
                                        '<td>',
                                            '<input class="{$prefix}-emailFromName" type="text" />',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td><div class="{$prefix}-emailFromEmailLabel">',
                                            'Your Email:',
                                        '</div></td>',
                                        '<td><div class="{$prefix}-emailFromEmailInputArea">',
                                            '<input class="{$prefix}-emailFromEmail" type="text" />',
                                        '</div></td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td colspan="2" width="100%" class="{$prefix}-addressBookLinkArea">',
                                            '<a href="javascript:void(0);" onclick="showPlaxoABChooser(\'{$prefix}-emailTo\', \'/media/plaxo_cb.html\'); return false;" class="{$prefix}-addressBookLink">',
                                                'Access your address books from Gmail, Yahoo, Outlook, and more...</a>',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td class="{$prefix}-emailToLabel" valign="top">To:</td>',
                                        '<td width="100%" class="{$prefix}-emailToInputArea">',
                                            '<textarea class="{$prefix}-emailTo" id="{$prefix}-emailTo" rows="2"></textarea>',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td class="{$prefix}-emailMessageLabel">Message:</td>',
                                        '<td class="{$prefix}-emailMessageInputArea">',
                                            '<textarea class="{$prefix}-emailMessage" rows="6" style="white-space: pre;"></textarea>',
                                        '</td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td colspan="2"><div class="{$prefix}-emailMakePublicArea">',
                                            '<input class="{$prefix}-emailMakePublic" type="checkbox" checked="checked"> Make this FlowGram publicly available',
                                        '</div></td>',
                                    '</tr>',
                                    '<tr>',
                                        '<td colspan="2">',
                                            '<div class="{$prefix}-emailSendButtonArea">',
                                                '<div class="{$prefix}-emailSendButton"></div>',
                                            '</div>',
                                        '</td>',
                                    '</tr>',
                                '</table>',
                            '</div>',
                            '<div class="{$prefix}-imForm {$prefix}-linkForm" style="display: none;">',
                                '<div class="{$prefix}-instructionsPage">',
                                    '<div class="{$prefix}-instructions"></div>',
                                    '<div class="{$prefix}-instructionsMakePublicArea">',
                                        '<input class="{$prefix}-instructionsMakePublic" type="checkbox" checked="checked"> Make this FlowGram publicly available',
                                    '</div>',
                                    '<div class="{$prefix}-continueButton"></div>',
                                '</div>',
                                '<div class="{$prefix}-urlPage">',
                                    '<div class="{$prefix}-urlInstructions">It\'s easy to show all your friends your FlowGrams!  Just copy it using ctrl-c (or command-c on Mac).</div>',
                                    '<div class="{$prefix}-urlLabel">URL: </div>',
                                    '<input class="{$prefix}-url" type="text" readonly="true" />',
                                '</div>',
                                '<div class="{$prefix}-linkPage">',
                                    '<div class="{$prefix}-linkInstructions">You can use the following HTML code to add a link to your FlowGram from your website, just copy it using ctrl-c (or command-c on Mac).</div>',
                                    '<div class="{$prefix}-linkLabel">HTML </div>',
                                    '<input class="{$prefix}-link" type="text" readonly="true" />',
                                '</div>',

                            '</div>',
                        '</div>',
                    '</div>',
                '</div>',
            '</div>',
            (inPanel ?
                '<div class="{$prefix}-altPrivacyControlsArea">' + privacyControls +
                    '</div></td></tr></table>' :
                ''),
        '</div>'
    ].join('');
};

// PRIVATE STATIC METHODS---------------------------------------------------------------------------

/**
 * Allocates a new ID.
 * @private
 * @return {Number} A new ID.
 */
SharingComponent.allocateId_ = function() {
    return SharingComponent.ID_++;
};
