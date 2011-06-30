/**
 * Copyright Flowgram Inc. 2007, all rights reserved.
 *
 * The ScaledImage class represents an image that can be scaled and cropped in various ways.
 *
 * @author Brian Westphal
 */

var ScaledImage = Class.create();

// TODO(westphal): Add optional support for automatic layout recalculation
// TODO(westphal): Add support for other modes like zoom-and-crop
// TODO(westphal): Unlisten for load event

Object.extend(ScaledImage.prototype, Component.prototype);
ScaledImage.superclass = Component;
ScaledImage.$super = Component.prototype;

Object.extend(ScaledImage.prototype, {
    /**
     * Initializes the ScaledImage.
     * @param {string} src The URL used to load the image.
     * @param {string} noSrc The image to load if there is no src image or if the src image fails to
     *     load.
     */
    initialize: function(src, noSrc) {
        ScaledImage.$super.initialize.call(this);

        /**
         * The URL used to load the image.
         * @type string
         * @private
         */
        this.src_ = src;
        
        /**
         * The URL of the image to load if no src is specified or if unable to load src.
         * @type string
         * @private
         */
        this.noSrc_ = noSrc;
    },

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    
    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_ScaledImage',
    
    /**
     * The source height of the image.
     * @type number
     * @private
     */
    height_: -1,
    
    /**
     * The image.
     * @type Element
     * @private
     */
    image_: null,
    
    /**
     * The source width of the image.
     * @type number
     * @private
     */
    width_: -1,
    
    // PUBLIC METHODS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        ScaledImage.$super.createDomElement.call(this);
        
        this.image_ = new Image();
        this.domElement_.appendChild(this.image_);
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        Event.observe(this.image_, 'load', this.handleLoad_.bindAsEventListener(this));
        Event.observe(this.image_, 'error', this.handleError_.bindAsEventListener(this));
        this.image_.style.visibility = 'hidden';
        this.image_.style.position = 'absolute';
        this.image_.src = this.src_ || this.noSrc_;

        // If no src or noSrc image was provided, remove the image element.
        if (!this.src_ && !this.noSrc_) {
            this.domElement_.removeChild(this.image_);
        }

        ScaledImage.$super.enterDom.call(this);
    },

    // PRIVATE METHODS------------------------------------------------------------------------------
    
    /**
     * Handles when the container is resized.
     * @private
     */
    handleContainerResized_: function() {
        var containerWidth = this.domElement_.offsetWidth;
        var containerHeight = this.domElement_.offsetHeight;
        var containerRatio = containerWidth / containerHeight;

        var width = this.width_;
        var height = this.height_;

        var imageRatio = width / height;

        // If the image is too wide.
        if (width > containerWidth) {
            width = containerWidth;
            height = width / imageRatio;
        }

        // If the image is too tall.
        if (height > containerHeight) {
            height = containerHeight;
            width = height * imageRatio;
        }

        // Repositioning/resizing the image within the container.
        this.image_.style.width = Math.floor(width) + 'px';
        this.image_.style.height = Math.floor(height) + 'px';
        this.image_.style.left = Math.floor((containerWidth - width) / 2) + 'px';
        this.image_.style.top = Math.floor((containerHeight - height) / 2) + 'px';
        this.image_.style.visibility = 'visible';
    },
    
    /**
     * Handles when there is an error loading the image.
     * @private
     */
    handleError_: function() {
        this.image_.src = this.noSrc_;
    },
    
    /**
     * Handles when the image is loaded.
     * @private
     */
    handleLoad_: function() {
        this.width_ = this.image_.width;
        this.height_ = this.image_.height;

        this.handleContainerResized_();
    }    
});
