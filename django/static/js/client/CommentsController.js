/**
 * @author Brian Westphal
 * 	Flowgram Client Comments Panel Controller
 */

var CommentsController = Class.create();

Object.extend(CommentsController.prototype, PanelController.prototype);
CommentsController.superclass = PanelController;
CommentsController.$super = PanelController.prototype;

Object.extend(CommentsController.prototype, {
    initialize: function(sendCallback){
        CommentsController.$super.initialize.call(this);

        /**
         * The comments.
         */
        this.commentsData_ = [];

        /**
         * The method to call when send is clicked.
         */
        this.sendCallback_ = sendCallback;
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    
    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_CommentsController',

    // PUBLIC METHODS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        CommentsController.$super.createDomElement.call(this);

        this.setContents(Component.newElementFromString(CommentsController.getHtmlString(),
                                                        {prefix: this.cssPrefix_}));
    },

    /**
     * Clears the comments.
     */
    clearComments: function() {
        var commentText = this.getSubElement('commentText');
        commentText.value = '';
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        this.registerClickHandlers({
            'sendButton': this.onSendClicked_.bindAsEventListener(this)
        });

        CommentsController.$super.enterDom.call(this);
    },

    /**
     * Gets the value of the comments.
     */
    getComments: function() {
        var commentText = this.getSubElement('commentText');
        return commentText.value;
    },

    /**
     * Sets the visibility of the component.
     * @param {boolean} visible True if to be made visible, false if invisible.
     * @param {number} offset The offset from the top of the page.
     */
	setVisible: function(visible, offset) {
        var style = this.domElement_.style;

        if (visible) {
            style.left = '0';
            style.top = offset + 'px';
            style.display = 'block';

            this.updateCommentsList_();

            window.setTimeout(this.periodicRefresh_.bind(this), 60000);
        } else {
            style.display = 'none';
        }

        // If the user is logged in, show the cell for adding comments.
        var username = window.g_FlashConnection.flex.getUsername() || 'anonymous'; // Added 'anonymous' to effectively disable this check (for now).
        var addCommentCell = this.getSubElement('addCommentCell');
        addCommentCell.style.display = username ? (Prototype.Browser.IE ? 'block' : 'table-cell') : 'none';
        var loginCell = this.getSubElement('loginCell');
        loginCell.style.display = username ? 'none' : (Prototype.Browser.IE ? 'block' : 'table-cell');
	},

    // PRIVATE METHODS------------------------------------------------------------------------------
    
    /**
     * Handles when comment data is received by the server.
     */
    onCommentDataReceivedFromServer_: function(transport) {
        this.commentsData_ = eval('(' + transport.responseText + ')');
        
        this.updateCommentsListUi_();
    },
    
    /**
     * Handles when the send button is clicked.
     */
    onSendClicked_: function() {
        if (this.getComments()) {
            this.sendCallback_();

            var username = window.g_FlashConnection.flex.getUsername();

            this.commentsData_.splice(
                0,
                0,
                {
                    'ownerUsername': username,
                    'ownerUrl': '/' + username,
                    'timeAgo': '0 minutes',
                    'text': this.getComments()
                });
            this.updateCommentsListUi_();

            this.clearComments();
        }
    },
    
    /**
     * If the control is visible, refreshes the contents.
     */
    periodicRefresh_: function() {
        var style = this.domElement_.style;
        if (style.display == 'block') {
            this.updateCommentsList_();

            window.setTimeout(this.periodicRefresh_.bind(this), 60000);
        }
    },
    
    /**
     * Updates the list of comments associated with the current flowgram.
     */
    updateCommentsList_: function() {
        var flowgramId = window.g_FlashConnection.flex.getCurrentFlowgramId();

        new Ajax.Request(
            '/api/getcomments/',
            {
                method: 'get',
                parameters: {
                    flowgram_id: flowgramId,
                    enc: 'json',
                    max: 25
                },
                onSuccess: this.onCommentDataReceivedFromServer_.bindAsEventListener(this)
            });
    },

    /**
     * Updates the UI for the comments list.
     */
    updateCommentsListUi_: function() {
        var commentsArea = this.getSubElement('commentsArea');
        commentsArea.innerHTML = '';

        if (this.commentsData_.length == 0) {
            commentsArea.innerHTML =
                '<div class="fg_disabled">No comments have been added.  Be the first to comment about this FlowGram!</div>';
        } else {
            this.commentsData_.each(function(comment) {
                commentsArea.appendChild(Component.newElementFromString(
                    CommentsController.getHtmlString_comment(comment),
                    {prefix: this.cssPrefix_}));
            });
        }
    }
});

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
CommentsController.getHtmlString = function() {
    return [
        '<div class="{$prefix}">',
            '<table class="{$prefix}-contentsLayoutTable"><tr>',
                '<td class="{$prefix}-commentsCell" valign="top">',
                    '<div class="fg_panelTitle">Comments &amp; Responses</div>',
                    '<div class="{$prefix}-commentsArea"></div>',
                '</td>',
                '<td class="{$prefix}-addCommentCell" valign="top">',
                    '<div class="fg_panelTitle">Post a Comment</div>',
                    '<textarea class="{$prefix}-commentText"></textarea>',
                    '<a class="{$prefix}-sendButton"><div class="fg_sendButton"></div></a>',
                '</td>',
                '<td class="{$prefix}-loginCell" valign="top">',
                    '<div class="fg_panelTitle">Post a Comment</div>',
                    'Please <a href="javascript: document.location.href = \'/login/?next=\' + document.location.href.replace(\'#\', \'%2523\') + \',p=comments\';">login</a> to post comments',
                '</td>',
            '</tr></table>',
        '</div>'
    ].join('');
};

/**
 * Gets the HTML string for a comment.
 * @param {Object} comment The data for the comment.
 * @return {string} The HTML string for a comment.
 */
CommentsController.getHtmlString_comment = function(comment) {
    return [
        '<table class="fg_commentsTable">',
            '<tr>',
                '<td class="fg_nameCell"><a href="', comment.ownerUrl, '">', comment.ownerUsername, '</a></td>',
                '<td class="fg_timeCell">', comment.timeAgo, ' ago</td>',
            '</tr>',
            '<tr><td colspan="2">',
                '<div class="hr"></div>',
                '<p>', comment.text, '</p>',
            '</td></tr>',
        '</table>'
    ].join('');
};
