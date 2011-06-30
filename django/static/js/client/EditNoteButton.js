/**
 * @author Chris Yap, Andrew Badr
 * 	Flowgram Edit Blank Page Button
 */

////
// This section for drag-and-drop is from: 
// http://www.webreference.com/programming/javascript/mk/column2/
//

var EditNoteButton = Class.create();

Object.extend(EditNoteButton.prototype, {
	initialize: function(save_callback, mode){
        this.MEDIA_PREFIX = '/media/images/';
        this.DEFAULT_LEFT_OFFSET = 5;
        this.DEFAULT_TOP_OFFSET = 5;

		// create div wrapper
        this.doc = document;
		this.div = this.doc.createElement('div');
        this.div.innerHTML = '<img src="'+this.MEDIA_PREFIX+'btn_edit.png"'+'>';

        // style the div wrapper
        var styles = this.div.style;
        styles.position = "absolute";
        styles.display = 'none';

		this.div.onclick = this.do_edit.bindAsEventListener(this);

        // insert it into the DOM
		this.doc.body.appendChild(this.div);
        
	},
	
	setPID: function(pid){
        this.pid = pid;
	},
	
	show: function(ypos){
        this.div.style.top = (ypos + this.DEFAULT_TOP_OFFSET) + 'px';
        this.div.style.left = this.DEFAULT_LEFT_OFFSET + "px";
        this.div.style.display = 'block';
	},
	
	hide: function(){
		this.div.style.display = 'none';
	},
	
	getHeight: function(){
        return 0;
	},

    do_edit : function(){
        document.location = "/bp/edit/?pid=" + this.pid;
    }
	
});
