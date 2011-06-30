/**
 * Flowgram client microphone setup instructions panel.  This panel is static and simply includes
 * some instructions and a button to continue setting up the microphone.
 * @author Brian Westphal
 */

var MicSetupInstructions = Class.create();

Object.extend(MicSetupInstructions.prototype, Component.prototype);
MicSetupInstructions.superclass = Component;
MicSetupInstructions.$super = Component.prototype;

Object.extend(MicSetupInstructions.prototype, {
    /**
     * Initialized the MicSetupInstructions panel.
     * @param {Function} continueCallback The callback function when continue is pressed.
     */
	initialize: function(continueCallback) {
        MicSetupInstructions.$super.initialize.call(this);

        this.continueCallback_ = continueCallback;
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    
    /**
     * The callback function when continue is pressed.
     * @type Function
     * @private
     */
    continueCallback_: null,

    /**
     * {@inheritDoc}
     */
    cssPrefix_: 'fg_MicSetupInstructions',

    // PUBLIC METHODS-------------------------------------------------------------------------------

    /**
     * {@inheritDoc}
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(MicSetupInstructions.getHtmlString(),
                                                          {prefix: this.cssPrefix_});
    },

    /**
     * {@inheritDoc}
     */
    enterDom: function() {
        var continueButton = this.getSubElement('continueButton');
        Event.observe(continueButton, 'click', this.continueCallback_);

        MicSetupInstructions.$super.enterDom.call(this);
    },

    /**
     * Sets whether or not the instructions are visible.
     * @param {boolean} visible True if the instructions are to be made visible, false if invisible.
     */
    setVisible: function(visible) {
        // If the instructions are not already added to the DOM, create the DOM element and add
        // them.
        if (visible && !this.domElement_) {
            this.createDomElement();
            document.body.appendChild(this.domElement_);
            this.enterDom();
        }

        var style = this.domElement_.style;

        if (visible) {
            style.display = 'block';
        } else {
            style.display = 'none';
        }
    }
});

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the widget, based on the style configuration.
 * @return {string} The HTML string for the widget.
 */
MicSetupInstructions.getHtmlString = function() {
    return [
        '<div class="{$prefix}">',
            '<!--<div class="{$prefix}-title">Recording Set Up</div>-->',
            '<div class="{$prefix}-contents">',
				'<div class="{$prefix}-instructionsImage">',
	                '<div class="{$prefix}-instructionsImageLeft"></div>',
		            '<div class="{$prefix}-instructionsImageRight"></div>',
		            '<div class="clearer"></div>',
				'</div>',
                '<p><strong>On this screen, you need to grant permission to access your ',
                'microphone.</strong></p>',
                '<ol class="{$prefix}-steps">',
                    '<li>Click <b>"Allow"</b>',
                    '<li>Click <b>"Remember"</b>',
                    '<li>Click <b>"Close"</b>',
                '</ol>',
                '<div class="{$prefix}-continueButton"></div>',
                '<a class="{$prefix}-helpLink" href="/help/">Need some help?</a>',
            '</div>',
        '</div>'
    ].join('');
};
