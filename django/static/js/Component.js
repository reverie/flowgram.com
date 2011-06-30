/**
 * Copyright Flowgram Inc. 2007, all rights reserved.
 *
 * The Component class represents an abstract UI component.
 *
 * @author Brian Westphal
 */

var Component = Class.create();

Object.extend(Component.prototype, {
    /**
     * Initializes the Component.
     */
    initialize: function() {
        /**
         * The child Components.
         * @type Array.<Component>
         */
        this.children_ = [];
    },

    // PRIVATE FIELDS-------------------------------------------------------------------------------
    
    /**
     * The css class prefix.
     * @type String
     * @private
     */
    cssPrefix_: 'fg',

    /**
     * The DOM element.
     * @type Element
     * @private
     */
    domElement_: null,

    /**
     * Denotes whether or not the component is in the DOM.
     * @type boolean
     * @private
     */
    inDom_: false,

    // PUBLIC METHODS-------------------------------------------------------------------------------

    /**
     * Adds a child component.  This method does not add the child component to the DOM.  After
     * calling this method, if the child is not already in the DOM, one should manually add the
     * component's root DOM element to the dom and then call enterDom.
     * @param {Component} child The child component.
     */
    addChild: function(child) {
        this.children_.push(child);
    },

    /**
     * Creates the DOM element for the component.  Methods that override this method should
     * generally not call this method.
     */
    createDomElement: function() {
        // If the DOM element is already created, exit early.
        if (this.domElement_) {
            return;
        }

        this.domElement_ = document.createElement('div');
    },

    /**
     * Dispatches the specified event type out of the DOM element for this component.
     * @param {String} type The type of event to fire.
     * @param {Object} opt_data The data to send.
     */
    dispatchEvent: function(type, opt_data) {
        this.getDomElement().fire('widget:' + type, opt_data);
    },

    /**
     * Called when the widget is to enter the DOM.  When overridding this method, be sure to call
     * this method at the end of the overridding method.
     */
    enterDom: function() {
        // If already in the DOM, exit early.
        if (this.isInDom()) {
            return;
        }

        this.inDom_ = true;

        // If the DOM element has not been created yet, create it.
        this.getDomElement();

        // Recursively calling enterDom for child Components.
        this.children_.each(function(child) {
            child.enterDom();
        });
    },
    
    /**
     * Called when the widget is to exit the DOM.  When overridding this method, be sure to call
     * this method at the beginning of the overridding method.
     */
    exitDom: function() {
        // If not already in the DOM, exit early.
        if (!this.isInDom()) {
            return;
        }

        this.inDom_ = false;

        // Recursively calling exitDom for child Components.
        this.children_.each(function(child) {
            child.exitDom();
        });
    },

    /**
     * Gets the CSS class prefix for the component.
     * @param {string} opt_field An optional field that, if specified, will be separated from the
     *     prefix by a hyphen (e.g. if the prefix is "fg" and field is "body", the result of this
     *     method would be "fg-body").
     * @return {string} The CSS class prefix.
     */
    getCssPrefix: function(opt_field) {
        return this.cssPrefix_ + (opt_field ? '-' + opt_field : '');
    },

    /**
     * Gets the root DOM element for the component.
     * @return {Element} The root DOM element for the component.
     */
    getDomElement: function() {
        if (!this.domElement_) {
            this.createDomElement();
        }

        return $(this.domElement_);
    },

    /**
     * Gets a sub-element by its class name where the specified field is passed to the getCssPrefix
     * method to retrieve the full CSS class name for the element.
     * @param {string} field The CSS class name field for the sub-element.
     * @return {Element} The sub-element or null if not found.
     */
    getSubElement: function(field) {
        var element = this.getDomElement().getElementsByClassName(this.getCssPrefix(field));
        return element && element[0] || null;
    },

    /**
     * The same as getSubElement.
     */
    $: function(field) {
        return this.getSubElement(field);
    },

    /**
     * Determines whether or not the component is in the DOM.
     * @return {boolean} True if the component is part of the DOM, false otherwise.
     */
    isInDom: function() {
        return this.inDom_;
    },

    /**
     * Registers an event handler with the DOM element for this component.
     * @param {String} type The type of event to fire.
     * @param {Function} handler The handler function.
     * @param {boolean} opt_capture If true, capture mode is used instead of bubbling.
     */
    observe: function(type, handler, opt_capture) {
        this.getDomElement().observe('widget:' + type, handler, opt_capture);
    },

    /**
     * Registers click handles for the specified buttons.
     * @param {Object} buttons The buttons.  Keys are the names of elements (which must be
     *     sub-elements).  Values are the handlers.  The handlers are not automatically bound.
     */
    registerClickHandlers: function(buttons) {
        for (var buttonName in buttons) {
            var button = this.getSubElement(buttonName);
            button.observe('click', buttons[buttonName]);
        }
    },

    /**
     * Removes a child component.
     * @param {Component} child The child component.
     * @param {boolean} removeFromDom If true, exit document is called and then the component's
     *     element is removed from the DOM.  If the specified component is not a child of this
     *     component, this parameter is ignored.
     * @return {boolean} True if a child was actually removed.
     */
    removeChild: function(child, removeFromDom) {
        var indexOfChild = this.children_.indexOf(child);
        if (indexOfChild >= 0) {
            // If the child was found.

            this.children_.splice(indexOfChild, 1);
            
            // If the child is to be removed from the DOM (and it is currently in the DOM).
            if (removeFromDom && child.isInDom()) {
                child.exitDom();

                // If the child DOM element has been created.
                var childElement = child.getDomElement();
                if (childElement) {
                    // If the child element has a parent element.
                    var parentNode = childElement.parentNode;
                    if (parentNode) {
                        parentNode.removeChild(childElement);
                    }
                }
            }
            
            return true;
        } else {
            // If the child was not found.
            
            return false;
        }
    },
    
    /**
     * Adds the component to the DOM inside the specified parent.  By default, this method adds to
     * the end of the parent's child list.  It can also be used to insert before a specified element
     * or to replace a specified element.  This method called enterDom for this component but does
     * NOT call exitDom even if the removed elements are represented by Components, this must be
     * done manually.
     * @param {HTMLElement} parentElement_ The parent element.
     * @param {boolean} opt_beforeOrReplaceElement If specified, the element to render the new
     *     element before or the element to be replaced.
     * @param {boolean} opt_replace If true, and opt_beforeOrReplaceElement is specified, the
     *     element specified in opt_beforeOrReplaceElement is replaced with this component's DOM
     *     element.  If false, and opt_beforeOrReplaceElement is specified, this component's DOM
     *     element is inserted after the element specified in opt_beforeOrReplaceElement.
     *     Otherwise, this parameter is ignored.
     */
    render: function(parentElement, opt_beforeOrReplaceElement, opt_replace) {
        var domElement = this.getDomElement();

        if (opt_beforeOrReplaceElement) {
            parentElement[opt_replace ? 'replaceChild' : 'insertBefore'].call(
                parentElement,
                domElement,
                opt_beforeOrReplaceElement);
        } else {
            parentElement.appendChild(domElement);
        }

        this.enterDom();
    },
    
    /**
     * Sets the CSS class prefix for the Component.  If one is going to use this method, it should
     * be called before the DOM element is created.
     * @param {string} cssPrefix The CSS class prefix.
     */
    setCssPrefix: function(cssPrefix) {
        this.cssPrefix_ = cssPrefix;
    },

    /**
     * Unregisters an event handler with the DOM element for this component.
     * @param {String} type The type of event to fire.
     * @param {Function} handler The handler function.
     */
    stopObserving: function(type, handler) {
        this.getDomElement().stopObserving('widget:' + type, handler);
    }
});

/**
 * Creates a new element from the specified HTML string.  The opt_values parameter can be used to
 * replace strings like "{$key}" with real values.
 * @param {String} htmlString Describes the element to be created.  If more then one root-level DOM
 *     element is described, only the first will be returned.
 * @param {Object} opt_values Keyed values to be replaced.  Keys are treated as regular expression
 *     strings, so be careful with naming.
 */
Component.newElementFromString = function(htmlString, opt_values) {
    // If values are specified, replacing the keys in the HTML string with the specified values.
    if (opt_values) {
        for (var key in opt_values) {
            var regexp = new RegExp('\\{\\$' + key + '\\}', 'g');
            htmlString = htmlString.replace(regexp, opt_values[key]);
        }
    }

    // Creating the DOM element.
    var tempDiv = document.createElement('div');
    tempDiv.innerHTML = htmlString;
    var element = tempDiv.firstChild;
    tempDiv.removeChild(element);    

    return $(element);
};
