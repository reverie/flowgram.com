/**
 * @author Chris Yap
 * 	Flowgram System Messages Controller
 */

var SystemMessagesController = Class.create();

Object.extend(SystemMessagesController.prototype, {
	initialize: function() {
		
	},
	
	initSystemMessages: function() {
		
		// if there are system messages present, grab them from the array set in base.html and pass them to the insertMessage method
		this.system_messages = '';
		for (var i=0; i < messages_array.length; i++) {
			this.system_messages = this.system_messages + messages_array[i] + '<br/>';
		}
		this.insertMessage(this.system_messages);
		
	},
	
	insertMessage: function(message_text) {
		
		// create message and message wrapper
		this.message_wrapper = document.createElement('div');
		Element.addClassName(this.message_wrapper, 'wrapper_message_module');
		this.message_wrapper.style.visibility = 'hidden';
		
		this.message = document.createElement('div');
		Element.addClassName(this.message, 'message_module');
		this.message.innerHTML = message_text + '<br/><br/><span class="continue">&raquo; Click anywhere to continue &laquo;</span>';
		this.message_wrapper.appendChild(this.message);
		
		// insert into DOM
		$('wrapper_messages').appendChild(this.message_wrapper);
		
		// set message position based on viewport
		var viewport_y_offset = getScrollY();
		var viewport_height = getWindowHeight();
		var module_height = this.message_wrapper.getHeight();
		this.message_wrapper.style.top = viewport_y_offset + (viewport_height/2) - module_height + 'px';
		this.message_wrapper.style.display = 'none';
		this.message_wrapper.style.visibility = 'visible';
		new Effect.Grow(this.message_wrapper, {duration: .5});
		
		// set event to remove message
		this.removeMessageCache = this.fadeMessage.bindAsEventListener(this);
		Event.observe(document, 'click', this.removeMessageCache);
		
	},
	
	fadeMessage: function() {
		
		Event.stopObserving(document, 'click', this.removeMessageCache);
		new Effect.Shrink(this.message_wrapper, {duration: .5});
		setTimeout(this.removeMessage.bind(this), 1500);
		
	},
	
	removeMessage: function() {
		
		$('wrapper_messages').removeChild(this.message_wrapper);
		
	}
	
	
});