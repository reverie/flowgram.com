function frame_doc(frame) {
    return doc = frame.contentDocument || frame.contentWindow.document || frame.document;
}

function rec_subDocuments(doc, arr) {
    arr.push(doc);
    var docFrames = doc.getElementsByTagName('frame');
    var docIframes = doc.getElementsByTagName('iframe');
    for (var i=0; i<docFrames.length; i++) {
        var dFrame = docFrames[i];
        try {
            rec_subDocuments(frame_doc(dFrame), arr);
        }
		catch (err) {
		 var xxx = 'pass';
        //    alert("We don't have access to all iframes.");
		}
    }
    for (var i=0; i<docIframes.length; i++) {
        var dIframe = docIframes[i];
        try {
            rec_subDocuments(frame_doc(dIframe), arr);
        }
        catch(err) {
			var xxx= 'pass';
            //alert("We don't have access to all iframes.");
        }
    }
    return arr;
}

function getDoctype(doc) {
    if (doc.firstChild.publicId) {
        return "<!DOCTYPE html PUBLIC \"" + doc.firstChild.publicId + "\" \"" + 
            doc.firstChild.systemId + "\">";
    }
    if (doc.firstChild.nodeName == "#comment") {
        data = doc.firstChild.data;
        if (data.substring(0,5) == "CTYPE") {
            var base = "<!DO" + data;
            var tail = base.charAt(base.length-2) + base.charAt(base.length-1);
            if (tail == 'dt') {
                return base + "d\">";
            }
            if (tail == '/E') {
                return base + "N\">";
            }
            // add more cases here
        }
    }
    return "";
}

function htmlTag(doc) //from PPK
{
	var node = doc.documentElement;
	var atts = node.attributes;
	if (atts.length == 0) return '<html>';
	var writestring = '<html';
	for (var i=0;i<atts.length;i++)
	{
		if (atts[i].value && atts[i].value !='null') {
			writestring += ' ' + atts[i].name + '=' + atts[i].value;
		}
	}
	writestring += '>';
	return writestring;
}

function killJavaScript(doc) {
	var script_tags = doc.getElementsByTagName('script');
	//have to go backwards, because the array is dynamic..going forwards we'll only get every other one! -andrew
	for (var i = script_tags.length-1; i>=0; i--) {
	    var script_tag = script_tags[i];
	   // if (script_tag.id != 'hl_bm_script') {
	        script_tag.parentNode.removeChild(script_tag);
	   // }
	}
}

function killAllJavaScript() {
    var docs = rec_subDocuments(document, new Array());
    for (var i=0; i<docs.length; i++) {
        killJavaScript(docs[i]);
    } 
}

function getHTML(doc) {
    doctype = getDoctype(doc);
    start_html = htmlTag(doc);
    inner_html = doc.documentElement.innerHTML;
    end_html = '</html>';
    rendered_html = doctype + start_html + inner_html + end_html;
    return rendered_html;
}

function getCurrentYPos() { //taken from a website
    if (document.body && document.body.scrollTop)
      return document.body.scrollTop;
    if (document.documentElement && document.documentElement.scrollTop)
      return document.documentElement.scrollTop;
    if (window.pageYOffset)
      return window.pageYOffset;
    return 0;
  }

function smoothScrollStep(scroll_step, time_step, num_left) {
    if (num_left > 0) {
        window.scrollBy(0, scroll_step);
        var strCall = "smoothScrollStep(" + scroll_step + ", " + time_step + ", " + (num_left-1) + ")";
        setTimeout(strCall, time_step);
    }
}

function smoothScrollTo(node) {
    var STEPS = 25;
    var TIME = 400;
    var targetY = node.offsetTop-100;
    if (targetY < 0) { targetY = 0;}
    var currentY = getCurrentYPos();
    var scroll_step = parseInt((targetY-currentY)/STEPS);
    var time_step = parseInt(TIME/STEPS);
    smoothScrollStep(scroll_step, time_step, STEPS);
}
