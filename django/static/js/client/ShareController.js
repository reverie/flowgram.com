/**
 * @author Chris Yap
 * 	Flowgram Client Share Panel Controller
 */

var ShareController = Class.create();

Object.extend(ShareController.prototype, {
	initialize: function(close_panel){
		this.sharePanel_ = document.createElement('div');
		this.sharePanel_.id = 'wrapper_share_panel';
        document.body.appendChild(this.sharePanel_);

        this.closeButton_ = document.createElement('div');
        Element.addClassName(this.closeButton_, 'closeButton');
        this.sharePanel_.appendChild(this.closeButton_);
        this.closeButton_.observe('click', close_panel);

        this.sharingComponent_ = new SharingComponent(true);
        this.sharingComponent_.render(this.sharePanel_);
        this.hideSharePanel();

        var domElement = this.sharingComponent_.getDomElement();
        domElement.style.margin = '0px auto';
        domElement.style.width = '986px';
	},
	
    getSharingComponent: function() {
        return this.sharingComponent_;
    },
    
    setFlowgramData: function(flowgramId, isOwner, isLoggedIn, ownerName, ownerUrl, title,
                              description, isPublic) {
        this.sharingComponent_.setFlowgramData(flowgramId, isOwner, isLoggedIn, ownerName, ownerUrl,
            title, description, isPublic);
    },
    
    setInTutorialMode: function(inTutorialMode, opt_userEmailAddress) {
        this.sharingComponent_.setInTutorialMode(inTutorialMode, opt_userEmailAddress);
    },
    
	showSharePanel: function(ypos){
		var domElement = this.sharePanel_;
        domElement.style.left = '0px';
        domElement.style.top = ypos + 'px';
		domElement.style.visibility = 'visible';

        pageTracker._trackPageview('/toolbar/panels/share');
	},
	
	hideSharePanel: function(){
		var domElement = this.sharePanel_;		
		domElement.style.visibility  = 'hidden';
	},
	
	getPanelHeight: function(){
		var domElement = this.sharePanel_;
		return Element.getHeight(domElement);
	}
});
