/**
 * @author Brian Westphal
 * Sharing Component
 */

var HeartRating = Class.create();

Object.extend(HeartRating.prototype, Component.prototype);
HeartRating.superclass = Component;
HeartRating.$super = Component.prototype;

/**
 * The HeartRating represents a rating indicator/controller.
 */
Object.extend(HeartRating.prototype, {
    /**
     * Initializes the component.
     */
	initialize: function(flowgramId, userFavorite, userCanRate) {
        HeartRating.$super.initialize.call(this);

        /**
         * The ID of the Flowgram.
         * @private
         * @type String
         */
        this.flowgramId_ = flowgramId;

        /**
         * Whether or not the fg is a favorite in the database.
         * @private
         * @type Boolean
         */
		this.isUserFavorite_ = userFavorite;
		
		 /**
         * Whether or not the heart is highlighted.
         * @private
         * @type Boolean
         */
		this.highlighted_ = userFavorite;
		
		 /**
         * Whether or not the user has permission to favorite.
         * @private
         * @type Boolean
         */
		this.userCanRate_ = userCanRate;
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_HeartRating',

    // PUBLIC METHODS-------------------------------------------------------------------------------
    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(HeartRating.getHtmlString(),
                                                          { prefix: this.cssPrefix_ });
        this.updateRating_(false);
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        if (this.userCanRate_) {
            this.domElement_.observe('mouseout', this.onMouseOut_.bindAsEventListener(this));
            this.domElement_.observe('mousedown', this.onMouseDown_.bindAsEventListener(this));
            this.domElement_.observe('mouseover', this.onMouseOver_.bindAsEventListener(this))
        }
    },

    // PRIVATE METHODS------------------------------------------------------------------------------
	updateRating_: function(updateDatabase) {
		if (updateDatabase) {
	        var builtInToken = $('csrf_token')
	        var token = builtInToken && builtInToken.innerHTML;
			
			if (this.highlighted_) {
				new Ajax.Request('/api/addfavorite/', {
					parameters: {
						flowgram_id: this.flowgramId_,
						csrfmiddlewaretoken: token
					}
				});
				this.isUserFavorite_ = true;
			} else {
				new Ajax.Request('/api/removefavorite/', {
					parameters: {
						flowgram_id: this.flowgramId_,
						csrfmiddlewaretoken: token
					}
				});
				this.isUserFavorite_ = false;
			}
		}
		
		var heart = this.getDomElement();
		
		if (this.highlighted_) {
			heart.addClassName(this.getCssPrefix('full'));
			heart.removeClassName(this.getCssPrefix('empty'));
		} else {
			heart.addClassName(this.getCssPrefix('empty'));
			heart.removeClassName(this.getCssPrefix('full'));
		}			
	},

	UnHighlight_: function(callUpdate) {
		this.highlighted_ = false;			
		this.updateRating_(callUpdate);
	},
	
	Highlight_: function(callUpdate) {
		this.highlighted_ = true;
		this.updateRating_(callUpdate);	
	},

	RemoveFavorite_: function() {
		this.UnHighlight_(false);
		this.updateRating_(true);
	},

	AddFavorite_: function() {
		this.Highlight_(false);
		this.updateRating_(true);
	},

    onMouseDown_: function(ev) {
		this.justRated_ = true;

		if (this.isUserFavorite_) {
			this.RemoveFavorite_();
		} else {
			this.AddFavorite_();
		}
    },
    
    onMouseOut_: function(ev) {
		this.justRated_ = false;
		if (!this.isUserFavorite_) {
			this.UnHighlight_(false);
		} else {
			this.Highlight_(false);
		}
    },
	
	onMouseOver_: function(ev) {
		if (this.justRated_) return;
		if (!this.isUserFavorite_) {
			this.Highlight_(false);
		} else {
			this.UnHighlight_(false);
		}
	}
    
});

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
HeartRating.getHtmlString = function() {
    return '<div class="{$prefix} {$prefix}-empty"></div>';
};

