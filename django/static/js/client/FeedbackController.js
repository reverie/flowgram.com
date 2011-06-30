/**
 * @author Brian Westphal
 * Flowgram Feedback Panel Controller
 */

var FeedbackController = Class.create();

Object.extend(FeedbackController.prototype, Component.prototype);
FeedbackController.superclass = Component;
FeedbackController.$super = Component.prototype;

/**
 * The FeedbackController represents a UI controller class for the feedback form.  The feedback form
 * is available in both playback and recording modes.  It should try to detect the URL that the user
 * is viewing (but allow them to change it or remove the URL entirely if desired -- for privacy or
 * if the feedback is unrelated to the current URL).  It should also automatically detect the user's
 * OS when possible.  The email address should be retrieved from the currently logged in user, if
 * there is a current user.  The details field will not be filled in automatically.
 */
Object.extend(FeedbackController.prototype, {
    /**
     * Initializes the controller.
     * @param {Object} detected An object with the following fields: url, email, os, and browser.
     * @param {Function} sendCallback The callback function when the send button is pressed.
     */
	initialize: function(detected, sendCallback, closePanel) {
        FeedbackController.$super.initialize.call(this);

        /**
         * The callback function for closing the panel.
         * @type Function
         * @private
         */
        this.closePanel_ = closePanel;

        /**
         * The information detected about the users environment.  See method comment for description
         * of fields.
         * @type Object
         * @private
         */
        this.detected_ = detected;

        /**
         * The callback function when the send button is pressed.
         * @type Function
         * @private
         */
        this.sendCallback_ = sendCallback;
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_FeedbackController',

    // PUBLIC METHODS-------------------------------------------------------------------------------
	
    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(FeedbackController.getHtmlString(),
                                                          {prefix: this.cssPrefix_});

        this.createCloseButton_();
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        // Registering the click action for the send button to perform a callback.
        var sendButton = this.getSubElement('send');
        Event.observe(sendButton, 'click', this.handleSendClicked_.bindAsEventListener(this));

        FeedbackController.$super.enterDom.call(this);
    },

    /**
     * @return {string} The comments.
     */
    getComments: function() {
        return this.getSubElement('comments').value;
    },

    /**
     * @return {string} The email address.  The user may clear this field for anonymity.
     */
    getEmail: function() {
        return this.getSubElement('email').value;
    },

    /**
     * @return {number} The height of the component in pixels.
     */
	getHeight: function() {
		return Element.getHeight(this.domElement_);
	},

    /**
     * @return string The system information including the operating system and web browser.  The
     *     user can actually enter anything here, but these are the suggested fields.
     */
    getSystemInfo: function() {
        return this.getSubElement('sysInfo').value;
    },

    /**
     * @return string The URL of the current page.  The user may clear/alter this field for privacy
     *     or if it does not pertain to the specific feedback being given.
     */
    getUrl: function() {
        return this.getSubElement('url').value;
    },

    /**
     * Sets the URL of the page that the user is currently viewing.
     * @param {string} url The URL of the page that the user is currently viewing.
     */
    setUrl: function(url) {
        this.detected_.url = url;
    },

    /**
     * Sets the visibility of the component.
     * @param {boolean} visible True if to be made visible, false if invisible.
     * @param {number} offset The offset from the top of the page.
     */
	setVisible: function(visible, offset) {
        var style = this.domElement_.style;

        if (visible) {
            style.left = '0px';
            style.top = offset + 'px';
            style.display = 'block';

            // Getting the email address from the detected values.
            var email = this.getSubElement('email');
            email.value = this.detected_.email || '';

            // Getting the current page URL from the detected values.
            var url = this.getSubElement('url');
            url.value = this.detected_.url || '';

            // Getting the system info from the detected values.
            var sysInfo = this.getSubElement('sysInfo');
            sysInfo.value = [
                'Operating System: ',
                (this.detected_.os || 'unknown'),
                "\nWeb Browser: ",
                (this.detected_.browser || 'unknown')
            ].join('');

            // Clearing the comments field.
            var comments = this.getSubElement('comments');
            comments.value = '';
        } else {
            style.display = 'none';
        }
	},

    // PRIVATE METHODS------------------------------------------------------------------------------

    createCloseButton_: function() {
        this.closeButton_ = document.createElement('div');
        Element.addClassName(this.closeButton_, 'closeButton');
        this.domElement_.appendChild(this.closeButton_);
        this.closeButton_.observe('click', this.closePanel_);
    },

    /**
     * Handles clicked events for the send button.
     * @private
     */
    handleSendClicked_: function() {
        var email = this.getSubElement('email');
        var comments = this.getSubElement('comments');
        if (email.value && comments.value) {
            this.sendCallback_();
        } else {
            window.alert('The email and comments fields are required.');
        }
    }
});

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
FeedbackController.getHtmlString = function() {
    return [
        '<div class="{$prefix}">',
			
			'<div class="{$prefix}-wrapper">',
			
				'<div class="{$prefix}-contact_methods">',
				
					'<div class="{$prefix}-title">Want to report a bug, need help, or have a suggestion?  Choose the feedback method that works best for you.</div>',
				
					'<div class="{$prefix}-method">',
						'<a href="/about_us/contact_us/email/">Email</a><br/>Send us a quick note.',
					'</div>',
			
					'<div class="{$prefix}-method">',
						'<span class="{$prefix}-chat_title">Chat</span><br/>',
						'<div id="{$prefix}-chat_text">Need help right away?  You can chat with us if we&#039;re online.  Click on the talk bubble.</div>',
						'<iframe src="http://www.google.com/talk/service/badge/Show?tk=z01q6amlqptjf6s5pju0flu3srj5gmker2e68sa2mqalab001t131amr46l7mfk4rofebv1nfjqooh2aoi0g94ur23dnpjmeu3j4jh3f5r99v1f5fpkrml3qgd6i6r2oukklrvqgevk2fjlq11id7nqhjme7cg1pb77jrasia&amp;w=146&amp;h=60" frameborder="0" allowtransparency="true" width="146" height="60"></iframe>',
						'<div class="clearer"></div>',
					'</div>',
					'<div class="{$prefix}-method"><a href="/help/">FAQ</a><br/>A collection of helpful frequently asked questions.</div>',
				'</div>',
				
				'<div class="divider_vert"></div>',
			
				'<div class="{$prefix}-report_bug">',
		            '<div class="{$prefix}-title">Report Bug</div>',
            
		            '<label for="{$prefix}-email">Email Address (required)</label>',
		            '<input class="{$prefix}-email" type="text">',

		            '<label for="{$prefix}-url">URL</label>',
		            '<input class="{$prefix}-url" type="text">',

		            '<label for="{$prefix}-sysInfo">System Details</label>',
		            '<textarea class="{$prefix}-sysInfo" rows="4"></textarea>',

		            '<label for="{$prefix}-comments">Comments (required)</label>',
		            '<textarea class="{$prefix}-comments" rows="10"></textarea>',

		            '<div class="{$prefix}-send"></div>',
				'</div>',
			
				'<div class="clearer"></div>',
				
			'</div>',

        '</div>'
    ].join('');
};
