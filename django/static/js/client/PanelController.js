/**
 * @author Brian Westphal
 * 	Flowgram Client Comments Panel Controller
 */

var PanelController = Class.create();

Object.extend(PanelController.prototype, Component.prototype);
PanelController.superclass = Component;
PanelController.$super = Component.prototype;

Object.extend(PanelController.prototype, {
    initialize: function(sendCallback){
        PanelController.$super.initialize.call(this);
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------

    closeButton_: null,

    // PUBLIC METHODS------------------------------------------------------------------------------- 
    
    /**
     * {@inheritDoc}
     * Panels that inherit from this method should call this method.
     */
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(PanelController.getHtmlString(),
                                                          {prefix: this.cssPrefix_});

        this.createCloseButton_();
    },

    /**
     * Gets the height of the panel.
     * @return {Number} The height, in pixels, of the panel.
     */
    getHeight: function() {
        return this.domElement_.offsetHeight;
    },

    /**
     * Sets the contents of the panel.
     * @param {Element} contentsElement The contents element.
     */
    setContents: function(contentsElement) {
        var contents = this.getSubElement('contents');
        contents.innerHTML = '';
        
        if (contentsElement) {
            contents.appendChild(contentsElement);
        }
    },

    // PRIVATE METHODS------------------------------------------------------------------------------

	createCloseButton_: function() {
        this.closeButton_ = document.createElement('div');
        Element.addClassName(this.closeButton_, 'fg_closeButton');
        this.domElement_.appendChild(this.closeButton_);
        this.closeButton_.observe('click',
                                  function() { window.g_FlashConnection.flex.closePanels(); });
    }
});

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
PanelController.getHtmlString = function() {
    return [
        '<div class="fg_PanelController">',
            '<div class="fg_PanelController-contents {$prefix}-contents"></div>',
        '</div>'
    ].join('');
};
