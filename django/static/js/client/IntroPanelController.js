/**
 * @author Brian Westphal
 * Intro Panel Controller
 */

var IntroPanelController = Class.create();

Object.extend(IntroPanelController.prototype, Component.prototype);
IntroPanelController.superclass = Component;
IntroPanelController.$super = Component.prototype;

/**
 * The IntroPanelController represents the controller class for the intro panel.
 */
Object.extend(IntroPanelController.prototype, {
    /**
     * Initializes the controller.
     */
	initialize: function() {
        IntroPanelController.$super.initialize.call(this);
	},

    // PRIVATE METHODS------------------------------------------------------------------------------

    /**
     * Gets the data for the flowgram from the server.
     * @private
     */
    getFlowgramDataFromServer_: function() {
        new Ajax.Request(
            '/api/getfg/' + this.username_ + '/' + this.flowgramId_ + '/',
            {
                parameters: {enc: 'json'},
                onSuccess: this.onFlowgramDataReceivedFromServer_.bindAsEventListener(this)
            });
    },
    
    /**
     * Handles when flowgram data is received from the server.
     * @param {Object} transport The event to be handled.
     * @private
     */
    onFlowgramDataReceivedFromServer_: function(transport) {
        this.flowgram_ = eval('(' + transport.responseText + ')');
    }
});
