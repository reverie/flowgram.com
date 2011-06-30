/**
 * @author Chris Yap, Andrew Badr
 * 	Flowgram Client Note Controller
 */

////
// This section for drag-and-drop is from: 
// http://www.webreference.com/programming/javascript/mk/column2/
//



var dragObject  = null;
var mouseOffset = null;

function getPosition(e){
	var left = 0;
	var top  = 0;

	while (e.offsetParent){
		left += e.offsetLeft;
		top  += e.offsetTop;
		e     = e.offsetParent;
	}

	left += e.offsetLeft;
	top  += e.offsetTop;

	return {x:left, y:top};
}

function mouseCoords(ev){
	if(ev.pageX || ev.pageY){
		return {x:ev.pageX, y:ev.pageY};
	}
	return {
		x:ev.clientX + document.body.scrollLeft - document.body.clientLeft,
		y:ev.clientY + document.body.scrollTop  - document.body.clientTop
	};
}

function getMouseOffset(target, ev){
	ev = ev || window.event;

	var docPos    = getPosition(target);
	var mousePos  = mouseCoords(ev);
	return {x:mousePos.x - docPos.x, y:mousePos.y - docPos.y};
}



function mouseMove(ev){
	ev           = ev || window.event;
	var mousePos = mouseCoords(ev);

	if(dragObject){
		dragObject.style.position = 'absolute';
		dragObject.style.top      = mousePos.y - mouseOffset.y + "px";
        dragObject.style.right    = '';
		dragObject.style.left     = mousePos.x - mouseOffset.x + "px";

		return false;
	}
}

function mouseUp(){
	dragObject = null;
}

function makeDraggable(item){
	if(!item) {return;}
	item.onmousedown = function(ev){
		dragObject  = this;
		mouseOffset = getMouseOffset(this, ev);
		return true;
	};
}

document.onmousemove = mouseMove;
document.onmouseup   = mouseUp;


////
// Start of our code
//
//

function ie6() {
    // cobbled together from PPK's browser detect code
    if (!Prototype.Browser.IE) {
        return false;
    }
    
    var versionSearchString = 'MSIE';

    //this function is from PPK
	var searchVersion = function (dataString) {
		var index = dataString.indexOf(versionSearchString);
		if (index == -1) return;
		return parseFloat(dataString.substring(index+versionSearchString.length+1));
	};

    var version = searchVersion(navigator.userAgent)
			|| searchVersion(navigator.appVersion)
			|| "an unknown version";

    if (version < 7) {
        return true;
    }
    return false;
}

var NoteController = Class.create();

Object.extend(NoteController.prototype, {
	initialize: function(save_callback, mode){
        //if (window.console && window.console.log) {
        //    window.console.log("NoteController.initialize received");
        //}
        this.DEFAULT_HEIGHT = 100;
        this.DEFAULT_WIDTH = 280;
        this.MEDIA_PREFIX = '/media/images/notes/';
        this.inEditMode_ = false;

        this.html = [
            '<table height="100%" width="100%" cellpadding="0" cellspacing="0">',
            '<tr id="note_top_row"><td><table width="100%" cellpadding="0" cellspacing="0" style="table-layout:fixed;">',
            '<tr><td width="6px" height="6pxpx" style="background-image: url(', this.MEDIA_PREFIX, 'upper_left.png);"></td>',
            '<td height="6px" style="background-image: url(', this.MEDIA_PREFIX, 'upper_center.png);"></td>',
            '<td width="9px" height="6px" style="background-image: url(', this.MEDIA_PREFIX, 'upper_right.png);"></td></tr>',
            '</table></td></tr><tr>',
            '<td height="100%"><table cellpadding="0" cellspacing="0" style="table-layout:fixed;" width="100%" height="100%">',
            '<tr><td width="6px" style="background-image: url(', this.MEDIA_PREFIX, 'mid_left.png);"></td>',
            '<td style="background-image: url(', this.MEDIA_PREFIX, 'note_m.png);" valign="top" width="100%" height="100%">',
            '<div id="note_center_div" style="margin-top: -8px; margin-left: 3px; padding-right: 3px; height:100%; width:100%;">',
            '</div></td><td width="9px" style="background-image: url(', this.MEDIA_PREFIX, 'mid_right.png);"></td></tr>',
            '</table></td></tr><tr><td>',
            '<table cellpadding="0" cellspacing="0" style="table-layout:fixed;" width="100%">',
            '<tr><td width="6px" height="9px" style="background-image: url(', this.MEDIA_PREFIX, 'lower_left.png);"></td>',
            '<td height="9px" style="background-image: url(', this.MEDIA_PREFIX, 'lower_center.png);"></td>',
            '<td width="9px" height="9px" style="background-image: url(', this.MEDIA_PREFIX, 'lower_right.png);"></td></tr>',
            '</table></td></tr></table>'].join('');
        
        this.DEFAULT_TEXT = "Click here to add a note to your page";
        this.DEFAULT_RIGHT_OFFSET = 70;
        this.DEFAULT_TOP_OFFSET = 30;
        this.MAX_NOTE_HEIGHT = 400;

        if (mode=='playback') {
            this.mode = mode;
        }
        else {
            this.mode = 'record';
        }
        
		// create div wrapper
        this.doc = document;
		this.div = this.doc.createElement('div');
        this.div.innerHTML = this.html;

        // style the div wrapper
        var styles = this.div.style;
        styles.position = "absolute";
        styles.right = this.DEFAULT_RIGHT_OFFSET + "px";
        styles.top = "0px"; //this will get overridden before it is ever displayed
        styles.display = 'none';

        // keep references to outer and innermost divs 
        this.outerContainer = this.div;
        this.innerContainer = this.outerContainer.getElementsByTagName('div')[0];

        // One of these *must* be 'auto' or else the cursor won't show up in FF over an iframe:
        // See: https://bugzilla.mozilla.org/show_bug.cgi?id=167801
        this.innerContainer.style.overflowY = "hidden";
        this.innerContainer.style.overflowX = "auto";
		
		// fill it in -- must come after we "keep references to outer..."
		this.createAnnotationModule();

        // resize it -- must come after createAnnotationModule
        this.resize();
		
        // keep reference to callback function
        this.save_callback = save_callback || function() {console.log('save callback');};

        // insert it into the DOM
		this.doc.body.appendChild(this.div);
        
	},
	
	createAnnotationModule: function(){
        
        // Create textarea for display of note
        var textarea_annotation = $(this.doc.createElement('textarea'));
        textarea_annotation.name = "annotation";
        textarea_annotation.onclick = this.edit_mode.bindAsEventListener(this);
        if (!ie6()){
            textarea_annotation.onkeyup = this.resize.bindAsEventListener(this);
        }
        textarea_annotation.value = this.DEFAULT_TEXT;

        // Style the textarea
        var ta_style = textarea_annotation.style;
        ta_style.resize = 'none';
        ta_style.fontSize = '12px';
        ta_style.lineHeight = '19px';
        ta_style.marginTop = '21px';
        ta_style.fontFamily = "Arial, sans-serif";
        ta_style.backgroundColor = "#fefebd";
        ta_style.overflow = 'hidden';
        ta_style.color = "gray";

        // Make save button
        var save_span = this.doc.createElement('span');
        var save_img = this.doc.createElement('img')
        save_img.src =  this.MEDIA_PREFIX + 'note_save.png';
        save_span.appendChild(save_img);
        var sss = save_span.style;
        sss.position = "absolute";
        sss.right = "12px";
        sss.bottom = "12px";
        sss.cursor = "pointer";
        this.save_button = save_span;
        save_span.onclick = this.write.bindAsEventListener(this);
        this.outerContainer.appendChild(save_span);

        // Make delete button
        var delete_span = this.doc.createElement('span');
        delete_span.onclick = this.deleteNote.bindAsEventListener(this);
        delete_span.appendChild(this.doc.createTextNode('Delete'));
        var dss = delete_span.style;
        dss.position = "absolute";
        dss.right="9px";
        dss.top = "3px";
        dss.cursor = "pointer";
        dss.fontSize ="11px";
        dss.fontWeight = "bold";
        dss.fontFamily = "Arial, sans-serif";
        dss.color = "#006080";
        this.delete_button = delete_span;
        this.outerContainer.appendChild(delete_span);
       
        // Make close button
        var close_span = this.doc.createElement('span');
        close_span.onclick = this.closeNote.bindAsEventListener(this);
        close_span.appendChild(this.doc.createTextNode('X'));
        var css = close_span.style;
        css.position = "absolute";
        css.right="5px";
        css.top = "-3px";
        css.fontFamily = "serif";
        css.color = "red";
        css.fontWeight = "bold";
        css.fontSize = "20px";
        css.cursor = "pointer";
        this.close_button = close_span;
        this.outerContainer.appendChild(close_span);

        // Flowgram branding title
        var title_span = this.doc.createElement('span');
        title_span.appendChild(this.doc.createTextNode('Flowgram Note'));
        var tss = title_span.style;
        tss.position = "absolute";
        tss.left = "6px";
        tss.top = "3px";
        tss.fontFamily = "Arial, sans-serif";
        tss.fontSize = "11px";
        tss.fontWeight = "bold";
        tss.color = "#666";
        this.title_bar = title_span;
        this.outerContainer.appendChild(title_span);
        
        // Insert it into the DOM
        this.innerContainer.appendChild( textarea_annotation );

        // keep references to field
        this.annotation_input = textarea_annotation;
        this.annotation_input.observe('blur', this.blur.bindAsEventListener(this));
	},
	
    focus: function() {
        this.edit_mode();
    },

    blur: function() {
        this.inEditMode_ = false;
    },
    
	setAnnotation: function(annotation){
        //if (window.console && window.console.log) {
        //    window.console.log("NoteController.setAnnotation received");
        //}

        if ((annotation == '') && (this.mode == 'record')) {
            annotation = this.DEFAULT_TEXT;
            this.annotation_input.style.color = "gray";
        }
        else {
            this.annotation_input.style.color = "black";
        }

        this.annotation_input.value = annotation;
        this.resize();
	},
	
	getAnnotation: function(){
        if (this.annotation_input.value == this.DEFAULT_TEXT && this.mode == 'record') {
            return '';
        }
		return this.annotation_input.value;
	},
	
    edit_mode: function(){
        if (this.inEditMode_) {
            return;
        }
        
        this.inEditMode_ = true;

        // Block editing if we are in playback mode:
        if (this.mode == 'playback') {
            return true;
        }
        // Otherwise, first remove the default value
        if (this.annotation_input.value == this.DEFAULT_TEXT) {
            this.annotation_input.value = '';
            this.annotation_input.style.color = "black";
        }

        // Enable the form field
        this.annotation_input.style.background = "#fefebd";
        //this.annotation_input.style.background = "transparent";
        this.annotation_input.style.border = "1px dashed #ddb";
        this.annotation_input.readOnly = false;
        this.save_button.style.display = "inline";
        this.delete_button.style.display = "none";

        window.setTimeout(
            function() {
                this.annotation_input.focus();
                this.annotation_input.select();
            }.bind(this),
            250);

        return true;
    },


    save_mode: function(){
        this.fullResize();
        this.annotation_input.style.background = "transparent";
        if (this.mode == 'record') {
            this.annotation_input.style.border = "0";
        }

        this.annotation_input.readOnly = true;
        this.save_button.style.display = "none";
        this.delete_button.style.display = "inline";
        return false;
    },

    write: function() {
        this.save_mode();
        this.save_callback();
        return false;
    },

    deleteNote : function(){
        this.annotation_input.value = "";
        this.write();
    },

    closeNote : function(){
        this.resize();    
        this.hide();
    },
	
	show: function(ypos, playback){
        //if (window.console && window.console.log) {
        //    window.console.log("NoteController.show called with (" + ypos + ', ' + playback + ')');
        //}

        if (playback) {
            this.mode = 'playback';
        }
        else {
            this.mode = 'record';
        }

        if (this.mode == 'playback') {
            this.annotation_input.style.border = "0";
            this.annotation_input.style.borderTop = "2px dotted #bbb";
        }

        this.save_mode();
        this.div.style.top = (ypos + this.DEFAULT_TOP_OFFSET) + 'px';
        this.div.style.right = this.DEFAULT_RIGHT_OFFSET + "px";
        this.div.style.display = 'block';
        this.resize(); //TODO(andrew): remove this call to resize

        // Set up drag&drop:
        var oc = this.outerContainer;
        var di = this.annotation_input;
        if (this.mode == 'playback'){
            oc.style.cursor = "move";
            di.style.cursor = "move";
            this.delete_button.style.display = "none";
            this.close_button.style.display = "inline";
            makeDraggable(oc);
        } else {
            //oc.style.cursor = "text";
            //di.style.cursor = "text";
            oc.style.cursor = "";
            di.style.cursor = "";
            this.close_button.style.display = "none";
            this.delete_button.style.display = "inline";
            oc.onmousedown = null;
        }
	},
	
    resize: function() {
        //if (window.console && window.console.log) {
        //    window.console.log("NoteController.resize call received.");
        //}

        var outer_style = this.outerContainer.style;

        // If the textarea is overflowing, resize the outer container
        //     to accomodate the larger contents.
        var new_width = (this.outerContainer.clientWidth + 
                                this.annotation_input.scrollWidth -
                                this.annotation_input.clientWidth);
        new_width = Math.max(new_width, this.DEFAULT_WIDTH);
        outer_style.width = new_width + "px";
        this.annotation_input.style.width = (new_width - 40) + "px";

        var new_height = (this.outerContainer.clientHeight + 
                                this.annotation_input.scrollHeight -
                                this.annotation_input.clientHeight);
        new_height = Math.max(new_height, this.DEFAULT_HEIGHT);
        if (new_height > this.MAX_NOTE_HEIGHT) {
            new_height = this.MAX_NOTE_HEIGHT;
            this.annotation_input.style.overflowY = "auto";
        }
        else {
            this.annotation_input.style.overflowY = "hidden";
        }
        outer_style.height = new_height + "px";
        this.annotation_input.style.height = (new_height - 45) + "px";
    },

    fullResize: function(){
        var outer_style = this.outerContainer.style;

        // Shrink the outer container to its default minimum size
        outer_style.width = this.DEFAULT_WIDTH + "px";
        outer_style.height = this.DEFAULT_HEIGHT + "px";
        this.resize();

        // This second resize necessary or else the bottom half of the last line can get cut off.
        // Not sure why. -andrew
        this.resize();

    },

	hide: function(){
		this.div.style.display = 'none';
	},
	
	getHeight: function(){
        return 0;
	}
	
});
