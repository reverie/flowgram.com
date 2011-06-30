/**
 * @author Brian Westphal
 * Flowgram Client Help Bubble Controller
 */

var HelpBubble = Class.create();

Object.extend(HelpBubble.prototype, Component.prototype);
HelpBubble.superclass = Component;
HelpBubble.$super = Component.prototype;

Object.extend(HelpBubble.prototype, {
    initialize: function(){
        HelpBubble.$super.initialize.call(this);

        this.render(document.body);
        this.setVisible(false);
	},

    // PRIVATE FIELDS-------------------------------------------------------------------------------

    autohideTimeout_: 0,

    cssPrefix_: 'fg_helpbubble',

    usingBottomArrow_: false,

    // PUBLIC METHODS------------------------------------------------------------------------------- 
    
    createDomElement: function() {
        this.domElement_ = Component.newElementFromString(HelpBubble.getHtmlString(),
                                                          {prefix: this.cssPrefix_});

        this.domElement_.observe('mouseover', this.onMouseOver_.bindAsEventListener(this));
        this.domElement_.observe('mouseout', this.onMouseOut_.bindAsEventListener(this));
    },

    enterDom: function() {
        HelpBubble.$super.enterDom.call(this);

        this.$('closeButton').observe('click',
                                      this.onCloseButtonClicked_.bindAsEventListener(this));
        this.$('dontShowTips').observe('click',
                                       this.onDontShowTipsClicked_.bindAsEventListener(this));
        this.$('nextTip').observe('click', this.onNextTipClicked_.bindAsEventListener(this));
    },

    setInstructions: function(instructions) {
        this.$('instructions').innerHTML = instructions;
    },

    /**
     * Sets the bounds of the target at which the bubble should point.  These are relative to the
     * top-left of the browser view pane.
     */
    setTargetBounds: function(targetX, targetY, targetWidth, targetHeight) {
        var targetRight = targetX + targetWidth;
        var targetBottom = targetY + targetHeight;
        
        var viewport = document.viewport;

        var element = this.$('table');

        var elementWidth =
            element.offsetWidth - HelpBubble.SHADOW_WIDTH_LEFT - HelpBubble.SHADOW_WIDTH_RIGHT;
        var elementHeight =
            element.offsetHeight - HelpBubble.SHADOW_HEIGHT_TOP - HelpBubble.SHADOW_HEIGHT_BOTTOM;
        var totalElementHeight = elementHeight + HelpBubble.ARROW_HEIGHT;

        // Determining whether to use an up arrow (on the top) or a down arrow (on the bottom).
        this.usingBottomArrow_ = targetBottom + totalElementHeight > viewport.getHeight();

        // Calculating the box bounds.
        var centerX = targetX + targetWidth / 2;

        var elementX = 
            HelpBubble.constrain(HelpBubble.SIDE_MARGIN,
                                 centerX - elementWidth / 2,
                                 viewport.getWidth() - elementWidth - HelpBubble.SIDE_MARGIN) -
            HelpBubble.SHADOW_WIDTH_LEFT;

        var elementY = targetY + (this.usingBottomArrow_ ?
                                      -totalElementHeight :
                                      targetHeight + HelpBubble.ARROW_HEIGHT);

        elementY = 
            HelpBubble.constrain(HelpBubble.ARROW_HEIGHT,
                                 elementY,
                                 viewport.getHeight() - totalElementHeight) +
            HelpBubble.ARROW_SHADOW_HEIGHT * (this.usingBottomArrow_ ? 1 : -1) -
            HelpBubble.SHADOW_HEIGHT_TOP;

        this.domElement_.style.left = Math.round(elementX) + 'px';
        this.domElement_.style.top = Math.round(elementY) + 'px';

        // Calculating the arrow position.
        var arrowX = HelpBubble.constrain(
            HelpBubble.ARROW_MARGIN,
            centerX - elementX - HelpBubble.ARROW_WIDTH / 2,
            elementWidth - HelpBubble.ARROW_WIDTH - HelpBubble.ARROW_MARGIN);

        var unusedArrow = this.$((this.usingBottomArrow_ ? 'up' : 'down') + 'Arrow');
        unusedArrow.style.visibility = 'hidden';

        var usedArrow = this.$((this.usingBottomArrow_ ? 'down' : 'up') + 'Arrow');
        usedArrow.style.visibility = 'visible';
        usedArrow.style.left = Math.round(arrowX) + 'px';
    },

    setTitle: function(title) {
        this.$('title').innerHTML = title;
    },

    setVisible: function(visible) {
        window.clearTimeout(this.autohideTimeout_);
        
        this.domElement_.style.visibility = visible ? 'visible' : 'hidden';

        if (!visible) {
            this.$('upArrow').style.visibility = 'hidden';
            this.$('downArrow').style.visibility = 'hidden';
        } else {
            var usedArrow = this.$((this.usingBottomArrow_ ? 'down' : 'up') + 'Arrow');
            usedArrow.style.visibility = 'visible';            
        }

        this.autohideTimeout_ =
            window.setTimeout(this.setVisible.bind(this, false), 10000);
    },

    // PRIVATE METHODS------------------------------------------------------------------------------

    onCloseButtonClicked_: function(ev) {
        g_FlashConnection.flex.helpBubbleCloseButtonClicked();
    },

    onDontShowTipsClicked_: function(ev) {
        g_FlashConnection.flex.helpBubbleDontShowTipsClicked();
    },

    onMouseOver_: function(ev) {
        window.clearTimeout(this.autohideTimeout_);
    },

    onMouseOut_: function(ev) {
        this.autohideTimeout_ =
            window.setTimeout(this.setVisible.bind(this, false), 10000);        
    },

    onNextTipClicked_: function(ev) {
        g_FlashConnection.flex.helpBubbleNextTipClicked();
    }
});

// PUBLIC STATIC FIELDS-----------------------------------------------------------------------------

HelpBubble.ARROW_HEIGHT = 26;

HelpBubble.ARROW_SHADOW_HEIGHT = 7;

HelpBubble.ARROW_SHADOW_WIDTH_LEFT = 8;

HelpBubble.ARROW_SHADOW_WIDTH_RIGHT = 8;

HelpBubble.ARROW_WIDTH = 36;

HelpBubble.CORNER_RADIUS = 4;

HelpBubble.SIDE_MARGIN = 24;

HelpBubble.SHADOW_HEIGHT_BOTTOM = 12;

HelpBubble.SHADOW_HEIGHT_TOP = 9;

HelpBubble.SHADOW_WIDTH_LEFT = 9;

HelpBubble.SHADOW_WIDTH_RIGHT = 9;

HelpBubble.ARROW_MARGIN = HelpBubble.SHADOW_WIDTH_LEFT + HelpBubble.CORNER_RADIUS -
    HelpBubble.ARROW_SHADOW_WIDTH_LEFT;

// PUBLIC STATIC METHODS----------------------------------------------------------------------------

HelpBubble.constrain = function(lowerBound, value, upperBound) {
    return Math.max(lowerBound, Math.min(value, upperBound));
};

/**
 * Gets the HTML string for the UI component.
 * @return {string} The HTML string for the component.
 */
HelpBubble.getHtmlString = function() {
    return [
        '<div class="{$prefix}">',
            '<table class="{$prefix}-table">',
                '<tr>',
                    '<td class="{$prefix}-tl"></td>',
                    '<td class="{$prefix}-t"></td>',
                    '<td class="{$prefix}-t"></td>',
                    '<td class="{$prefix}-tr"></td>',
                '</tr>',
                '<tr>',
                    '<td  class="{$prefix}-l"></td>',
                    '<td class="{$prefix}-contents">',
                        '<div class="{$prefix}-title"></div>',
                    '</td>',
                    '<td class="{$prefix}-contents" align="right" valign="top">',
                        '<div class="{$prefix}-closeButton"></div>',
                    '</td>',
                    '<td class="{$prefix}-r"></td>',
                '</tr>',
                '<tr>',
                    '<td class="{$prefix}-l"></td>',
                    '<td class="{$prefix}-contents" colspan="2">',
                        '<div class="{$prefix}-instructions"></div>',
                        '<table width="100%"><tr>',
                            '<td>',
                                '<div class="{$prefix}-dontShowTipsArea"><a href="javascript:void(0);" class="{$prefix}-dontShowTips">Don\'t Show Tips</a></div>',
                            '</td>',
                            '<td>',
                                '<div class="{$prefix}-nextTipArea"><a href="javascript:void(0);" class="{$prefix}-nextTip">Next Tip</a></div>',
                            '</td>',
                        '</tr></table>',
                    '</td>',
                    '<td class="{$prefix}-r"></td>',
                '</tr>',
                '<tr>',
                    '<td class="{$prefix}-bl"></td>',
                    '<td class="{$prefix}-b"></td>',
                    '<td class="{$prefix}-b"></td>',
                    '<td class="{$prefix}-br"></td>',
                '</tr>',
            '</table>',
            '<div class="{$prefix}-upArrow"></div>',
            '<div class="{$prefix}-downArrow"></div>',
        '</div>'
    ].join('');
};
