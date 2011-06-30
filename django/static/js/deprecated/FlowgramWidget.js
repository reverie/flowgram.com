/**
 * Copyright Flowgram Inc. 2007, all rights reserved.
 *
 * The FlowgramWidget class represents a UI component for displaying Flowgrams as teasers.  These
 * are embeddable into 3rd-party webpages and have several configuration options.
 *
 * @author Brian Westphal
 */

// TODO(westphal): separate scrolling text and transitionable image thing into other components
// TODO(westphal): only works in FF 2, check/implement fixes for other browsers

var FlowgramWidget = Class.create();

Object.extend(FlowgramWidget.prototype, Component.prototype);
FlowgramWidget.superclass = Component;
FlowgramWidget.$super = Component.prototype;

Object.extend(FlowgramWidget.prototype, {
    /**
     * Initializes the FlowgramWidget.
     * @param {string} username The username of the user who owns the flowgram to be displayed.
     * @param {string} flowgramId The ID of the flowgram to be shown.
     * @param {number} opt_style The style for the widget.
     */
    initialize: function(username, flowgramId, opt_style) {
        FlowgramWidget.$super.initialize.call(this);

        /**
         * The ID of the flowgram to be shown.
         * @type string
         * @private
         */
        this.flowgramId_ = flowgramId;

        /**
         * The style for the widget.
         * @type number
         * @private
         */
        this.style_ = opt_style || FlowgramWidget.DEFAULT_STYLE;

        /**
         * The username of the user who owns the flowgram to be displayed.
         * @type string
         * @private
         */
        this.username_ = username;

        // -----------------------------------------------------------------------------------------

        if (!this.checkStyleValidity_()) {
            throw new Error('Invalid style');
        }
    },

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    
    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_FlowgramWidget',
        
    /**
     * The current slide.
     * @type ScaledImage
     * @private
     */
    currentSlide_: null,
    
    /**
     * The flowgram data.
     * @type Object
     * @private
     */
    flowgram_: null,
    
    /**
     * The maximum number of frames per second for transitions.
     * @type number
     * @private
     */
    fps_: 30,
    
    /**
     * The next slide.
     * @type ScaledImage
     * @private
     */
    nextSlide_: null,

    /**
     * The index of the currently showing page.
     * @type number
     * @private
     */
    pageIndex_: -1,

    /**
     * The number of milliseconds between pages.
     * @type number
     * @private
     */
    timeBetweenPages_: 3000,

    /**
     * The height available for showing the title.
     * @type number
     * @private
     */
    titleAvailableHeight_: 0,

    /**
     * The width available for showing the title.
     * @type number
     * @private
     */
    titleAvailableWidth_: 0,

    /**
     * The height needed for the title (this may be scrolled).
     * @type number
     * @private
     */
    titleHeight_: 0,

    /**
     * The height needed for a single line of the title.
     * @type number
     * @private
     */
    titleLineHeight_: 0,

    /**
     * The time to pause when at the beginning and end of a title scroll.
     * @type number
     * @private
     */
    titleScrollPauseDuration_: 2000,

    /**
     * The number of pixels to scroll the title by, per second.
     * @type number
     * @private
     */
    titleScrollPps_: 30,

    /**
     * The time the title scrolling started.
     * @type number
     * @private
     */
    titleScrollStartTime_: 0,

    /**
     * The width needed for the title (this may be scrolled).
     * @type number
     * @private
     */
    titleWidth_: 0,

    /**
     * The time the current transition started.
     * @type number
     * @private
     */
    transitionStartTime_: 0,

    /**
     * The number of milliseconds to take for each transition.
     * @type number
     * @private
     */
    transitionDuration_: 500,

    // PUBLIC METHODS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(FlowgramWidget.getHtmlString(this.style_),
                                                          {prefix: this.cssPrefix_});

        var title = this.getSubElement('title');

        // If long titles should not wrap.
        if (title && !(this.style_ & FlowgramWidget.Style.LONG_TITLE_WRAP)) {
            title.style.whiteSpace = 'nowrap';
        }
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        this.calculateLayout_();

        this.getFlowgramDataFromServer_();

        FlowgramWidget.$super.enterDom.call(this);
    },

    // PRIVATE METHODS------------------------------------------------------------------------------
    
    /**
     * Calculates the layout.
     * @private
     */
    calculateLayout_: function() {
        // TODO(westphal): calculate 8
        var availableHeight = this.domElement_.offsetHeight - 8;

        var contents = this.getSubElement('contents');    
        var title = this.getSubElement('title');
        var titleContainer = this.getSubElement('titleContainer');
        var play = this.getSubElement('play');
        var summary = this.getSubElement('summary');

        // TODO(westphal): calculate 4
        // Adding bottom spacing if there are no parts under the contents.
        if (!title && !play && !summary) {
            availableHeight -= 4;
        }

        // Subtracting space needed for the title.
        if (title) {
            // Calculating the line height for titles.
            var realTitle = title.innerHTML;
            title.innerHTML = 'X';
            this.titleLineHeight_ = title.offsetHeight + 2;
            title.innerHTML = realTitle;
            
            // TODO(westphal): calculate 4
            // Getting the width and height needed for the title.
            this.titleWidth_ = title.offsetWidth + 4;
            this.titleHeight_ = title.offsetHeight;
            var useTitleHeight = this.titleHeight_;

            // If the title is more than 2 lines high, scroll vertically.
            if (this.titleHeight_ >
                    this.titleLineHeight_ * FlowgramWidget.MAX_NUM_VISIBLE_TITLE_LINES) {
                titleContainer.style.height = (this.titleLineHeight_ * 2) + 'px';
                useTitleHeight = titleContainer.offsetHeight;
            } else {
                titleContainer.style.height = this.titleHeight_ + 'px';
            }
            
            titleContainer.style.width = (this.domElement_.offsetWidth - 2) + 'px';
            
            // Getting the available width and height for showing the title.
            this.titleAvailableWidth_ = titleContainer.offsetWidth;
            this.titleAvailableHeight_ = titleContainer.offsetHeight;
            
            // TODO(westphal): calculate 4
            title.style.left = '4px';
            
            // TODO(westphal): This doesn't stop the title from scrolling if already started from a
            //                 previous call to calculateLayout_.
            // If necessary, starting to scroll the title.
            if (this.titleWidth_ > this.titleAvailableWidth_ ||
                    this.titleHeight_ > this.titleAvailableHeight_) {
                this.startScrollingTitle_();
            }
            
            // TODO(westphal): Calculate 4/8
            availableHeight -= useTitleHeight + (play || summary ? 4 : 8);
        }

        // Subtracting space needed for the controls.
        availableHeight -= Math.max(play && play.offsetHeight || 0,
                                    summary && summary.offsetHeight || 0);

        // Setting the height of the contents.
        contents.style.height = availableHeight + 'px';

        // TODO(westphal): calculate 4
        if (titleContainer) {
            titleContainer.style.top = (contents.offsetTop + contents.offsetHeight + 4) + 'px';
        }
    },
    
    /**
     * Checks to make the sure style of the widget is valid.
     * @return {boolean} True if valid, false if invalid.
     * @private
     */
    checkStyleValidity_: function() {
        var style = this.style_;
        var s = FlowgramWidget.Style;

        // Counting the number of transitions types that are selected.
        var numSetTransitionBits = (style & s.TRANSITION_CROSS_DISOLVE ? 1 : 0) +
                                   (style & s.TRANSITION_FADE_THROUGH_WHITE ? 1 : 0) +
                                   (style & s.TRANSITION_SLIDE ? 1 : 0);

        // Checking for explicit, exclusive, large or small; explicit, non-exclusive, title scroll
        // or wrap; and that zero or one transitions were selected.
        return (style & s.LARGE ^ style & s.SMALL) &&
               (style & s.LONG_TITLE_SCROLL | style & s.LONG_TITLE_WRAP) &&
               numSetTransitionBits <= 1;
    },
    
    /**
     * Gets the data for the flowgram from the server.
     * @private
     */
    getFlowgramDataFromServer_: function() {
        new Ajax.Request(
            '/api/getfg/' + this.username_ + '/' + this.flowgramId_ + '/',
            {
                parameters: {enc: 'json'},
                onSuccess: this.handleFlowgramDataReceivedFromServer_.bindAsEventListener(this)
            });
    },
    
    /**
     * Handles when flowgram data is received from the server.
     * @param {Object} transport The event to be handled.
     * @private
     */
    handleFlowgramDataReceivedFromServer_: function(transport) {
        this.flowgram_ = eval('(' + transport.responseText + ')');

        var play = this.getSubElement('play');
        if (play) {
            play.href = this.flowgram_.flex_url;
        }

        this.startSlideshow_();
    },
    
    /**
     * Shows the next slide.
     * @private
     */
    showNextSlide_: function() {
        // TODO(westphal): Check corner case where current transition hasnt finished
        // TODO(westphal): Check if image has been displayed for 3 seconds
        
        var numPages = this.flowgram_.pages.length;
        this.pageIndex_ = (this.pageIndex_ + 1) % numPages;
        
        this.nextSlide_ = new ScaledImage(this.flowgram_.pages[this.pageIndex_].thumb_url,
                                          '/media/images/thumbnailUnavailable.gif');
        this.addChild(this.nextSlide_);

        var slideElement = this.nextSlide_.getDomElement();
        slideElement.style.position = 'absolute';
        slideElement.style.visibility = 'hidden';
        slideElement.style.width = '100%';
        slideElement.style.height = '100%';

        var contents = this.getSubElement('contents');
        contents.appendChild(slideElement);
        this.nextSlide_.enterDom();

        this.startTransition_();

        // If there are more than 1 pages, start going through them.
        if (numPages > 1) {
            window.setTimeout(this.showNextSlide_.bind(this), this.timeBetweenPages_);
        }
    },
    
    /**
     * Starts scrolling the title.
     * @private
     */
    startScrollingTitle_: function() {
        this.titleScrollStartTime_ = new Date().getTime();
        this.updateTitleScroll_();
    },
    
    /**
     * Starts the slideshow.
     * @private
     */
    startSlideshow_: function() {
        // Pre-fetching thumbnail images (and getting the total duration).
        this.flowgram_.duration = 0;
        this.flowgram_.pages.each(function(page) {
            var image = new Image();
            if (page.thumb_url) {
                image.src = page.thumb_url;
            }

            this.flowgram_.duration += page.duration;
        }.bind(this));

        var title = this.getSubElement('title');
        if (title) {
            title.innerHTML = this.flowgram_.title;
        }

        // Building duration string.
        var hours = Math.floor(this.flowgram_.duration / 3600);
        var minutes = Math.floor(this.flowgram_.duration % 3600 / 60);
        var seconds = this.flowgram_.duration % 60;

        var time = (hours ? hours + ':' : '') +
                   (minutes < 10 ? '0' : '') + minutes + ':' +
                   (seconds < 10 ? '0' : '') + seconds;

        // Getting the number of pages.
        var numPages = this.flowgram_.pages.length;

        // TODO(westphal): localize/depluralize sometimes the pages string
        var summary = this.getSubElement('summary');
        if (summary) {
            summary.innerHTML = time + ' | ' + numPages + ' pages';
        }

        this.calculateLayout_();

        if (numPages > 0) {
            this.pageIndex_ = -1;
            this.showNextSlide_();
        }
    },
    
    /**
     * Starts the transition.
     * @private
     */
    startTransition_: function() {
        var nslideElement = this.nextSlide_.getDomElement();
        nslideElement.style.visibility = 'visible';

        this.transitionStartTime_ = new Date().getTime();
        this.updateTransition_();
    },
    
    /**
     * Updates the scrolling on the title.  The scroll pattern is as follows: 1.) pause for 2
     * seconds; 2.) scroll left until the right/bottom edge of the title is reached; 3.) pause for 2
     * seconds; 4.) scroll right until the left/top edge is reached.
     * @private
     */
    updateTitleScroll_: function() {
        var title = this.getSubElement('title');

        // The number of pixels that will change over the course of a scroll.
        var pixelsToScrollH = this.titleWidth_ - this.titleAvailableWidth_;
        var pixelsToScrollV = this.titleHeight_ - this.titleAvailableHeight_;

        // Determining if the left or top is to be scrolled.
        var pixelsToScroll;
        var property;
        var padding = 0;
        if (pixelsToScrollH > 0) {
            pixelsToScroll = pixelsToScrollH;
            property = 'left';
            padding = 4;
        } else {
            pixelsToScroll = pixelsToScrollV;
            property = 'top';
        }

        // The number of milliseconds it will take to scroll those pixels.
        var timeToScrollTitle = Math.floor(pixelsToScroll / (this.titleScrollPps_ / 1000));
        // The number of milliseconds it will take to execute the scroll pattern.
        var patternDuration = 2 * this.titleScrollPauseDuration_ + 2 * timeToScrollTitle;

        var timeChange = (new Date().getTime() - this.titleScrollStartTime_) % patternDuration;

        // TODO(westphal): calculate 4
        if (timeChange < this.titleScrollPauseDuration_) {
            // Pattern part 1: pausing.

            title.style[property] = padding + 'px';
        } else if (timeChange < this.titleScrollPauseDuration_ + timeToScrollTitle) {
            // Pattern part 2: scrolling to left.
            
            var progress = (timeChange - this.titleScrollPauseDuration_) / timeToScrollTitle;
            title.style[property] =
                Math.floor(padding - (progress * pixelsToScroll + padding)) + 'px';
        } else if (timeChange < 2 * this.titleScrollPauseDuration_ + timeToScrollTitle) {
            // Pattern part 3: pausing.
            
            title.style[property] = '-' + pixelsToScroll + 'px';
        } else {
            // Pattern part 4: scrolling to right.
            
            var progress = (timeChange - 2 * this.titleScrollPauseDuration_ - timeToScrollTitle) /
                           timeToScrollTitle;
            title.style[property] =
                Math.floor(padding - ((1 - progress) * pixelsToScroll + padding)) + 'px';
        }
        
        window.setTimeout(this.updateTitleScroll_.bind(this),
                          this.titleScrollPauseDuration_ / this.fps_);
    },
    
    /**
     * Updates the progress of the current transition.
     * @private
     */
    updateTransition_: function() {
        var progress = (new Date().getTime() - this.transitionStartTime_) /
                       this.transitionDuration_;
        var nslideElement = this.nextSlide_.getDomElement();

        if (progress >= 1) {
            // If the transition is complete.
        
            // If there is a current slide (there will not be in the starting case).
            if (this.currentSlide_) {
                var cslideElement = this.currentSlide_.getDomElement();
                this.removeChild(this.currentSlide_, true);
            }

            if (this.style_ & FlowgramWidget.Style.TRANSITION_SLIDE) {
                // If slide transition.
                
                nslideElement.style.left = '0';
            } else if (this.style_ & FlowgramWidget.Style.TRANSITION_CROSS_DISOLVE ||
                       this.style_ & FlowgramWidget.Style.TRANSITION_FADE_THROUGH_WHITE) {
                nslideElement.style.opacity = '1';
            }

            this.currentSlide_ = this.nextSlide_;
            this.nextSlide_ = null;
        } else {
            // If there is a current slide (there will not be in the starting case).
            if (this.currentSlide_) {
                var cslideElement = this.currentSlide_.getDomElement();

                if (this.style_ & FlowgramWidget.Style.TRANSITION_SLIDE) {
                    // If slide transition.

                    cslideElement.style.left = Math.floor(progress * -100) + '%';
                } else if (this.style_ & FlowgramWidget.Style.TRANSITION_CROSS_DISOLVE) {
                    cslideElement.style.opacity = 1 - progress;
                } else if (this.style_ & FlowgramWidget.Style.TRANSITION_FADE_THROUGH_WHITE) {
                    cslideElement.style.opacity = Math.max(0, 1 - progress * 2);
                }
            }

            if (this.style_ & FlowgramWidget.Style.TRANSITION_SLIDE) {
                // If slide transition.

                nslideElement.style.left = Math.floor(100 - progress * 100) + '%';
            } else if (this.style_ & FlowgramWidget.Style.TRANSITION_CROSS_DISOLVE) {

                nslideElement.style.opacity = progress;
            } else if (this.style_ & FlowgramWidget.Style.TRANSITION_FADE_THROUGH_WHITE) {
                if (progress >= 0.5) {
                    nslideElement.style.opacity = (progress - 0.5) * 2;
                } else {
                    nslideElement.style.opacity = 0;
                }
            }

            window.setTimeout(this.updateTransition_.bind(this), 1000 / this.fps_);
        }
    }
});

// PUBLIC STATIC FIELDS-----------------------------------------------------------------------------

/**
 * The maximum number of lines that should be made visible for titles (when wrapping mode is
 * enabled).
 * @type number
 */
FlowgramWidget.MAX_NUM_VISIBLE_TITLE_LINES = 2;

/**
 * The components that can be added to the widget to affect its appearance.
 * @enum {number}
 */
FlowgramWidget.Style = {
    LARGE: 1,
    LONG_TITLE_SCROLL: 2,
    LONG_TITLE_WRAP: 4,
    PLAY: 8,
    SMALL: 16,
    SUMMARY: 32,
    TITLE: 64,
    TRANSITION_CROSS_DISOLVE: 128,
    TRANSITION_FADE_THROUGH_WHITE: 256,
    TRANSITION_SLIDE: 512
};

/**
 * The default style: small, with title, long titles wrap and scroll, slide transitions.
 * @type number
 */
FlowgramWidget.DEFAULT_STYLE =
    FlowgramWidget.Style.SMALL |
    FlowgramWidget.Style.TITLE |
    FlowgramWidget.Style.LONG_TITLE_WRAP |
    FlowgramWidget.Style.LONG_TITLE_SCROLL |
    FlowgramWidget.Style.TRANSITION_SLIDE;

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the widget, based on the style configuration.
 * @param {number} style The style of the widget.
 * @return {string} The HTML string for the widget.
 */
FlowgramWidget.getHtmlString = function(style) {
    var controlsString =
        (style & (FlowgramWidget.Style.PLAY | FlowgramWidget.Style.SUMMARY) ?
            [
                (style & FlowgramWidget.Style.PLAY ? '<a class="{$prefix}-play">Play</a>' : ''),
                (style & FlowgramWidget.Style.SUMMARY ?
                    '<div class="{$prefix}-summary"></div>' : '')
            ].join('') :
            '');
                
    return [
        '<div class="{$prefix} {$prefix}-',
                (style & FlowgramWidget.Style.LARGE ? 'large' : 'small'),
                '">',
            '<div class="{$prefix}-contents"></div>',
            (style & FlowgramWidget.Style.TITLE ?
                '<div class="{$prefix}-titleContainer"><div class="{$prefix}-title"></div></div>' :
                ''),
            controlsString,
        '</div>'
    ].join('');
};
