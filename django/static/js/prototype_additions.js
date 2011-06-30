/*
Object.extend(Ajax.Request.prototype, {
  initialize: function(url, options) {
    this.transport = Ajax.getTransport();
    this.url = url;
    this.hasStarted = false;
    this.setOptions(options);
    if(!this.options.wait){
      this.start();
    }
  },
  start: function() {
  	if(!this.hasStarted) {
  	  this.hasStarted = true;
  	  this.request(this.url);
  	}
  },
  abort: function(){
  	this.transport.abort();
  }	
});

Object.extend(Ajax.Updater.prototype, {
   initialize: function(container, url, options) {
   	
    this.url = url;
	this.container = {
      success: (container.success || container),
      failure: (container.failure || (container.success ? null : container))
    }

    this.transport = Ajax.getTransport();
    this.setOptions(options);

    var onComplete = this.options.onComplete || Prototype.emptyFunction;
    this.options.onComplete = (function(transport, param) {
      this.updateContent();
      onComplete(transport, param);
    }).bind(this);
	if(!this.options.wait)
      this.start();
  },
  start: function() {
  	if(!this.hasStarted) {
  	  this.hasStarted = true;
  	  this.request(this.url);
  	}
  },
  abort: function(){
  	this.transport.abort();
  }	
});
*/

//Ajax.Updater.prototype.start = Ajax.Request.prototype.start;
//Ajax.Updater.prototype.abort = Ajax.Request.prototype.abort;

/**
 * Extended to make it easier to stopObserving when anonymous functions are used
 * as the observer.  Event.observe will now return an array containing all the 
 * stuff required to stop the observer.
 * Event.stopObserving has been extended to allow a single parameter to be passed in.
 * that parameter should be the array returned by Event.observe.
 */
Object.extend(Event, {_observe: Event.observe, _stopObserving: Event.stopObserving});
Object.extend(Event, {
	observe: function(element, name, observer, useCapture){
		Event._observe(element, name, observer, useCapture);
		return [element, name, observer, useCapture];
	},
	stopObserving: function(element, name, observer, useCapture){
	    if(arguments.length == 1){
	    	name = element[1];
	    	observer = element[2];
	    	useCapture = element[3];
	    	element = element[0];
	    }
		Event._stopObserving(element, name, observer, useCapture);
	}
});



/**
 * Define some globals for figuring out what type of element we have
 */

function Node() {}

Node.ELEMENT_NODE = 1;
Node.ATTRIBUTE_NODE = 2;
Node.TEXT_NODE = 3;
Node.CDATA_SECTION_NODE = 4;
Node.ENTITY_REFERENCE_NODE = 5;
Node.ENTITY_NODE = 6;
Node.PROCESSING_INSTRUCTION_NODE = 7;
Node.COMMENT_NODE = 8;
Node.DOCUMENT_NODE = 9;
Node.DOCUMENT_TYPE_NODE = 10;
Node.DOCUMENT_FRAGMENT_NODE = 11;
Node.NOTATION_NODE = 12;

/**
 * This section extends (or create in IE) the NodeList object
 * to allow for enumeration of read-only node lists (element.childNodes, etc)
 * A NodeList differs from an Array in a couple ways.
 * - It is specifically designed to hold Nodes (XML nodes or HTML elements)
 * - It is read only
 * - It is often "live" meaning that if the DOM changes, this list will often change
 *   without warning.
 * - It's much faster
 */
function IENodeList(node_list){
	var _real_node_list;
	this._real_node_list = node_list;
};

NodeList_Extensions = {
	elements:	function() {
					return this.inject([], function(elementNodes, element) {
					  if(element.nodeType == Node.ELEMENT_NODE)
						elementNodes.push(element);
					  return elementNodes;
					});
				},
	firstElement:	function(){
					return this.elements().first();
				},
	lastElement:	function(){
					return this.elements().last();
				},
	inspect:	Array.prototype.inspect				
};


Object.extend(IENodeList.prototype, Enumerable);
Object.extend(IENodeList.prototype, {
	_each:	function(iterator) {
		if(this._real_node_list){
			for (var i = 0; i < this._real_node_list.length; i++){
				iterator(this._real_node_list[i]);
			}
		}
	},
	first:		function(){ return this._real_node_list[0]; },
	last:		function(){ return this._real_node_list[this._real_node_list.length - 1]; },
	indexOf:	function(object) {
				for (var i = 0; i < this._real_node_list.length; i++)
					if (this._real_node_list[i] == object) return i;
				return -1;
			}
});
Object.extend(IENodeList.prototype, NodeList_Extensions);

if(typeof NodeList != 'undefined'){
	Object.extend(NodeList.prototype, Enumerable);	
	Object.extend(NodeList.prototype, {
		_each:		Array.prototype._each,
		first:		Array.prototype.first,
		last:		Array.prototype.last,
		indexOf:	Array.prototype.indexOf
	});
	Object.extend(NodeList.prototype, NodeList_Extensions);
}

/**
 * Build a browser independent NodeList object from a node list.
 * This does nothing in FireFox, but supplies a bunch of fixes in IE.
 */
function $NL(node_list){

	if(typeof IENodeList != 'undefined' || typeof node_list != 'NodeList'){
		return new IENodeList(node_list);
	}
	else{
		return node_list;
	}

}

/**
 * Cookie extensions
 */

var Cookie = {
  set: function(name, value, daysToExpire, pathString) {
    var expire = '';
    if (daysToExpire != undefined) {
      var d = new Date();
      d.setTime(d.getTime() + (86400000 * parseFloat(daysToExpire)));
      expire = '; expires=' + d.toGMTString();
    }
	var path = '';
	path = '; path=' + pathString;
    return (document.cookie = escape(name) + '=' + escape(value || '') + expire + path);
  },
  get: function(name) {
    var cookie = document.cookie.match(new RegExp('(^|;)\\s*' + escape(name) + '=([^;\\s]*)'));
    return (cookie ? unescape(cookie[2]) : null);
  },
  erase: function(name) {
    var cookie = Cookie.get(name) || true;
    Cookie.set(name, '', -1);
    return cookie;
  },
  accept: function() {
    if (typeof navigator.cookieEnabled == 'boolean') {
      return navigator.cookieEnabled;
    }
    Cookie.set('_test', '1');
    return (Cookie.erase('_test') === '1');
  }
};