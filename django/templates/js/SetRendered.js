var csrfmiddlewaretoken = '{{csrf_token}}';

function htmlTag(doc) { //derived from PPK
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

function rec_subDocuments(doc, arr) {
    arr.push(doc);
    return arr; // killed until we stabilize
    var docFrames = doc.getElementsByTagName('frame');
    var docIframes = doc.getElementsByTagName('iframe');
    for (var i=0; i<docFrames.length; i++) {
        var dFrame = docFrames[i];
        try {
            rec_subDocuments(frame_doc(dFrame), arr);
        }
        catch(err){
            var xxx = 'pass';
			//alert("We don't have access to all iframes.");
        }
    }
    for (var i=0; i<docIframes.length; i++) {
        var dIframe = docIframes[i];
        try {
            rec_subDocuments(frame_doc(dIframe), arr);
        }
        catch(err) {
			var xxx = 'pass';
            //alert("We don't have access to all iframes.");
        }
    }
    return arr;
}

function GetDocType(doc) {
    if(!doc) {
        doc = window.document;
    }
    
    // Firefox 
    if (doc.firstChild.publicId) {
        return "<!DOCTYPE html PUBLIC \"" + doc.firstChild.publicId + "\" \"" +
            doc.firstChild.systemId + "\">";
    }
    // IE: the docstring appears as an HTML comment node, with the first three and last two characters removed
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

function GetCurrentHTML(doc)
{
    if(!doc) {
        doc = document;
    }

    doctype = GetDocType(doc);
	if (doc.documentElement.outerHTML) {
		rendered_html = doctype + doc.documentElement.outerHTML;
		return rendered_html;
	}
	//else (non-IE):
    start_html = htmlTag(doc);
    inner_html = doc.documentElement.innerHTML;
    end_html = '</html>';
    rendered_html = doctype + start_html + inner_html + end_html;
    return rendered_html;
}

function KillJS(doc)
{
	var script_tags = doc.getElementsByTagName('script');
	//have to go backwards, because the array is dynamic..going forwards we'll only get every other one -andrew
	for(var i = script_tags.length - 2; i >= 0; i--) {
	    var script_tag = script_tags[i];
        if(script_tag.id != "fg_bookmarklet") {
            script_tag.parentNode.removeChild(script_tag);
        }
    }
}

function KillJSRec(doc)
{
    if(!doc) {
        doc = window.document;
    }

    var docs = rec_subDocuments(document, new Array());
    for(var i = 0; i < docs.length; i++) {
        KillJS(docs[i]);
    }
}

function setrendered() {
    
    KillJSRec();

    try {
        var formElem = document.createElement("form");
        formElem.method = "POST";
        formElem.action = window.parent.fg_host + "/api/setrendered/";
        formElem.target = '_self';
        formElem.style.visibility = "hidden";
        formElem.acceptCharset = 'UTF-8';
        formElem = document.body.appendChild(formElem);
        
/*
        var url = document.createElement("input");
        url.type = "hidden";
        url.name = "url";
        url.value = window.FGURL || window.location;
        formElem.appendChild(url);
*/

        var title = document.createElement("input");
        title.type = "hidden";
        title.name = "title";
        title.value = window.document.title;
        formElem.appendChild(title);

        var upid = document.createElement("input");
        upid.type = "hidden";
        upid.name = "upid";
        upid.value = window.parent.fg_upid;
        formElem.appendChild(upid);

        var flowgram_id = document.createElement("input");
        flowgram_id.type = "hidden";
        flowgram_id.name = "flowgram_id";
        flowgram_id.value = window.parent.fg_fgid;
        formElem.appendChild(flowgram_id);

        var html = document.createElement("input");
        html.type = "hidden";
        html.name = "html";
        html.value = GetCurrentHTML();
        formElem.appendChild(html);

        var csrf = document.createElement("input");
        csrf.type = "hidden";
        csrf.name = "csrfmiddlewaretoken";
        csrf.value = csrfmiddlewaretoken;
        formElem.appendChild(csrf);

        formElem.submit();
    } catch(err) {
        //alert(err.message);
    }
}

function trySetRendered() {
    var images = document.getElementsByTagName('img');
    var num_images = images.length;
    if (num_images == 0) {
        setrendered();
        return;
    }
    
    var last_image = images[num_images - 1];
    if (last_image.complete) {
        setrendered();
        return
    }
    
    last_image.onload = setrendered;
    setTimeout(setrendered, 3000);
}

if (!window.parent.fg_pageid) {
    //alert('No window.parent.fg_pageid found');
    // TODO(westphal): Replace dev.flowgram.com with correct domain.
}

trySetRendered();
