/**
 * @author Chris Yap
 * 	Flowgram Client iFrame Controller
 */

var ClientIFrameController = Class.create();

Object.extend(ClientIFrameController.prototype, {
	initialize: function(iframeID, iframeURL){
		
		this.iframeID = iframeID;
		this.iframeURL = iframeURL;
		this.wrapper = document.createElement('div');
		this.wrapper.id = 'wrapper_client_login';
		this.iframe = document.createElement('iframe');
		this.iframe.id = this.iframeID;
		this.iframe.name = this.iframeID;
		this.wrapper.appendChild(this.iframe);
	},
	
	showClientIFrame: function(ypos){
		
		this.wrapper.style.top = ypos + 'px';
		document.body.appendChild(this.wrapper);
		window.frames[this.iframeID].location = this.iframeURL;
		
	},
	
	hideClientIFrame: function(){
		
		document.body.removeChild(this.wrapper);
		
	}
	
	
});