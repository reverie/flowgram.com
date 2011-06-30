/**
 * @author Chris Yap
 * 	Flowgram Footer Controller
 */

var FooterController = Class.create();

Object.extend(FooterController.prototype, {
	initialize: function(){
		
		this.setFooterPositionCache = this.setFooterPosition.bindAsEventListener(this);
		
		// set footer position onload
		Event.observe(window, 'load', this.setFooterPositionCache);
		
		// set footer position on window resize
		Event.observe(window, 'resize', this.setFooterPositionCache);
		
		
	},
	
	// always lock footer to bottom of viewport, flowing with content
	setFooterPosition: function(){
		
		if (document.getElementById) {
			var windowHeight=document.viewport.getHeight();
			if (windowHeight>0) {
				
				var contentHeight = $('wrapper_content').offsetHeight + $('wrapper_header_main').offsetHeight + $('wrapper_header_sub').offsetHeight;
				var footerElement = $('wrapper_footer');
				var footerHeight=footerElement.offsetHeight + $('wrapper_bottom').offsetHeight;
				if (windowHeight-(contentHeight+footerHeight)>=0) {
					footerElement.style.position='relative';
					if ($$('div.generic_text')[0] != null && $$('div.generic_text')[0] != '') {
						if ((windowHeight-(contentHeight+footerHeight)-70)>=0) {
							footerElement.style.marginTop=(windowHeight-(contentHeight+footerHeight)-70)+'px';
						}
						else {
							footerElement.style.position='static';
							footerElement.style.marginTop = 10 + 'px';
						}
					}
					else {
						if ((windowHeight-(contentHeight+footerHeight)-40)>=0) {
							footerElement.style.marginTop=(windowHeight-(contentHeight+footerHeight)-40)+'px';
						}
						else {
							footerElement.style.position='static';
							footerElement.style.marginTop = 10 + 'px';
						}
					}
				}
				else {
					footerElement.style.position='static';
					footerElement.style.marginTop = 10 + 'px';
				}
			}
		}

		
	}
	
	
	
	
	
	
});