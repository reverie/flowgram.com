/**
 * @author Brian Westphal
 * Sharing Component
 */

var StarRating = Class.create();

Object.extend(StarRating.prototype, Component.prototype);
StarRating.superclass = Component;
StarRating.$super = Component.prototype;

/**
 * The StarRating represents a rating indicator/controller.
 */
Object.extend(StarRating.prototype, {
    /**
     * Initializes the component.
     */
	initialize: function(flowgramId, avgRating, userRating, userCanRate) {
        StarRating.$super.initialize.call(this);

        /**
         * The ID of the Flowgram.
         * @private
         * @type String
         */
        this.flowgramId_ = flowgramId;

        /**
         * The average rating across users.
         * @private
         * @type Number
         */
        this.avgRating_ = avgRating;

        /**
         * The rating by the current user.  Negative if n/a.
         * @private
         * @type Number
         */
        this.userRating_ = userRating;

        /**
         * Denotes whether or not the current user can rate the flowgram.
         */
        this.userCanRate_ = userCanRate;
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_StarRating',

    /**
     * Denotes if the flowgram was just rated.  The user has to mouse off and then on to rerate.
     * @private
     * @type Boolean
     */
    justRated_: false,

    /**
     * Denotes whether or not the user is currently rating the flowgram.  If this is true, the users
     * temporary rating is shown, rather than the average rating or the set user rating.
     * @private
     * @type Boolean
     */
    userCurrentlyRating_: false,

    /**
     * The user's rating, valid while the user is rating the flowgram.
     * @private
     * @type Number
     */
    userTempRating_: -1,

    // PUBLIC METHODS-------------------------------------------------------------------------------
	
    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(StarRating.getHtmlString(),
                                                          { prefix: this.cssPrefix_ });

        this.updateRating_();
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        if (this.userCanRate_) {
            this.domElement_.observe('mouseout', this.onMouseOut_.bindAsEventListener(this));
            this.domElement_.observe('mousedown', this.onMouseDown_.bindAsEventListener(this));
            
            var stars = this.getStars_();
            var numStars = stars.length;
            for (var starsIndex = 0; starsIndex < numStars; starsIndex++) {
                var star = stars[starsIndex];

                star.observe('mousemove', this.onMouseMove_.bindAsEventListener(this));
            }

            this.getSubElement('none').observe('mousemove',
                                               this.onMouseMove_.bindAsEventListener(this));
            this.getSubElement('full').observe('mousemove',
                                               this.onMouseMove_.bindAsEventListener(this));
        }
    },

    // PRIVATE METHODS------------------------------------------------------------------------------
    
    getStars_: function() {
        var stars = [];
        
        for (var starsIndex = 1; starsIndex <= StarRating.NUM_STARS; starsIndex++) {
            stars[starsIndex - 1] = this.getSubElement(starsIndex + '');
        }
        
        return stars;
    },

    indexOfStar_: function(currentStar) {
        var stars = this.getStars_();
        var numStars = stars.length;
        for (var starsIndex = 0; starsIndex < numStars; starsIndex++) {
            var star = stars[starsIndex];
            if (star == currentStar) {
                return starsIndex;
            }
        }

        return -1;
    },

    onMouseDown_: function(ev) {
        if (this.justRated_) {
            return;
        }

        this.userRating_ = this.userTempRating_;
        this.userCurrentlyRating_ = false;
        this.justRated_ = true;
        
        this.updateRating_();

        var builtInToken = $('csrf_token')
        var token = builtInToken && builtInToken.innerHTML ||
                    window.parent.g_FlashConnection.flex.getToken();

        new Ajax.Request(
            '/api/saverating/',
            {
                parameters: {
                    flowgram_id: this.flowgramId_,
                    rating: this.userRating_,
                    csrfmiddlewaretoken: token
                }
            });
    },

    onMouseMove_: function(ev) {
        if (this.justRated_) {
            return;
        }

        this.userCurrentlyRating_ = true;

        var currentStar = Event.element(ev);
        if (currentStar == this.getSubElement('none')) {
            this.userTempRating_ = 0;
            this.updateRating_();
            return;
        } else if (currentStar == this.getSubElement('full')) {
            this.userTempRating_ = StarRating.NUM_STARS;
            this.updateRating_();
            return;
        } else {
            currentStar = currentStar.parentNode;
        }

        var starIndex = this.indexOfStar_(currentStar);
        
        this.userTempRating_ = starIndex + 1;
        
        var relativeX = ev.pointerX() - currentStar.viewportOffset()[0];
        if (relativeX < currentStar.offsetWidth / 2) {
            this.userTempRating_ -= 0.5;
        }

        this.updateRating_();
    },
    
    onMouseOut_: function(ev) {
        if (Position.within(this.domElement_, ev.pointerX(), ev.pointerY())) {
            return;
        }

        this.userCurrentlyRating_ = false;
        this.justRated_ = false;
        this.updateRating_();
    },
    
    updateRating_: function() {
        var ratingToShow;
        var starType;

        if (this.userCurrentlyRating_) {
            // If the user is currently rating the flowgram.
        
            ratingToShow = this.userTempRating_;
            starType = StarRating.Stars_.CURRENT;
        } else {
            // If the user is not currently rating the flowgram.
            
            if (this.userRating_ >= 0) {
                // If the user has rated this flowgram.  Show the user's rating.

                ratingToShow = this.userRating_;
                starType = StarRating.Stars_.USER;
            } else {
                // If the user has not rated this flowgram.  Show the average rating.
                
                ratingToShow = this.avgRating_;
                starType = StarRating.Stars_.AVG;
            }
        }

        // Scaling and rounding the rating so that there are no half ratings.
        ratingToShow = Math.round(ratingToShow * 2);

        var prefixes = ['empty', 'avg', 'avgHalf', 'current', 'currentHalf', 'user', 'userHalf'];

        // Setting the stars.
        var stars = this.getStars_();
        var numStars = stars.length;
        for (var starsIndex = 0; starsIndex < numStars; starsIndex++) {
            var star = stars[starsIndex];

            // Removing current prefixes.
            prefixes.each(function(prefix) {
                              star.removeClassName(this.getCssPrefix(prefix));
                          }.bind(this));

            var fullValue = (starsIndex + 1) * 2;
            if (ratingToShow >= fullValue) {
                star.addClassName(this.getCssPrefix(starType));
            } else if (ratingToShow == fullValue - 1) {
                star.addClassName(this.getCssPrefix(starType + 'Half'));
            } else {
                star.addClassName(this.getCssPrefix('empty'));
            }
        }
    }
});

// PUBLIC STATIC FIELDS-----------------------------------------------------------------------------

StarRating.NUM_STARS = 5;

// PRIVATE STATIC FIELDS----------------------------------------------------------------------------

StarRating.Stars_ = {
    AVG: 'avg',
    CURRENT: 'current',
    USER: 'current'
};

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
StarRating.getHtmlString = function() {
    return [
        '<div class="{$prefix}">',
			'<img class="{$prefix}-none" src="/media/images/spacer.gif" width="5" height="12" />',
            '<div class="{$prefix}-1 fg_StarRating-star fg_StarRating-empty"><img src="/media/images/spacer.gif"></div>',
            '<div class="{$prefix}-2 fg_StarRating-star fg_StarRating-empty"><img src="/media/images/spacer.gif"></div>',
            '<div class="{$prefix}-3 fg_StarRating-star fg_StarRating-empty"><img src="/media/images/spacer.gif"></div>',
            '<div class="{$prefix}-4 fg_StarRating-star fg_StarRating-empty"><img src="/media/images/spacer.gif"></div>',
            '<div class="{$prefix}-5 fg_StarRating-star fg_StarRating-empty"><img src="/media/images/spacer.gif"></div>',
			'<img class="{$prefix}-full" src="/media/images/spacer.gif" width="5" height="12" />',
        '</div>'
    ].join('');
};
