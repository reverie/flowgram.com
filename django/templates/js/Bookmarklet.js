var csrfmiddlewaretoken = '{{csrf_token}}';

var iframeReconstructionFunctionStrings = [];

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

function frame_doc(frame) {
    return frame.contentDocument;
}

function buildFrameReconstructionScript(frame) {
    var attributes = frame.attributes;
    
    var output = ['(function() { var frame = document.createElement("iframe");'];
    
    for (var attributesIndex = 0; attributesIndex < attributes.length; attributesIndex++) {
        var attribute = attributes[attributesIndex];

        if (attribute.value && attribute.value != 'null') {
            output.push('frame.', attribute.name, '="', attribute.value, '";');
        }
    }
    
    output.push('frame.contentDocument.innerHTML = "', frame_doc(frame).innerHTML.replace('"', '\\"').replace("'", "\\'"), '";');
    output.push('document.appendChild(frame);');
    
    output.push('})();');
    return output.join('');
}

function rec_subDocuments(doc) {
    var docIframes = doc.getElementsByTagName('iframe');
    for (var i=0; i<docIframes.length; i++) {
        var dIframe = docIframes[i];
        try {
            var frameDoc = frame_doc(dIframe);
            rec_subDocuments(frameDoc);

            var frameRecreationScript = buildFrameReconstructionScript(dIframe);
            
            var scriptPlaceholder = ['(fg_iframe_placeholder_string_id_',
                                     iframeReconstructionFunctionStrings.length,
                                     ')'].join('');
            
            var scriptNodeString = ['<script id="fg_bookmarklet" type="text/javascript">',
                                    frameRecreationScript,
                                    '</script>'].join('');
            iframeReconstructionFunctionStrings.push(scriptNodeString);
                        
            dIframe.parentNode.replaceChild(document.createTextNode(scriptPlaceholder), dIframe);
        }
        catch(err) {
			var xxx = 'pass';
            //alert("We don't have access to all iframes.");
        }
    }
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

    for (var iframesIndex = 0; iframesIndex < iframeReconstructionFunctionStrings.length; iframesIndex++) {
        var scriptPlaceholder = ['(fg_iframe_placeholder_string_id_', iframesIndex, ')'].join('');

        inner_html = inner_html.replace(scriptPlaceholder,
                                        iframeReconstructionFunctionStrings[iframesIndex]);
    }

    end_html = '</html>';
    rendered_html = doctype + start_html + inner_html + end_html;
    return rendered_html;
}

function KillJS(doc)
{
    return;
	var script_tags = doc.getElementsByTagName('script');
	//have to go backwards, because the array is dynamic..going forwards we'll only get every other one -andrew
	for(var i = script_tags.length - 1; i >= 0; i--) {
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

    KillJS(doc);

    rec_subDocuments(doc);
}

function addpage() {
    if(window.FGQA) {
        if (window.flowgram_quickadd_submitted) {
            return;
        }

        window.flowgram_quickadd_submitted = true;
    }
    
    KillJSRec();

    try {
        var formElem = document.createElement("form");
        formElem.method = "POST";
        formElem.style.visibility = "hidden";
        formElem.acceptCharset = 'UTF-8';
        formElem = document.body.appendChild(formElem);
        
        if(!window.FGQA) {
            formElem.action = "http://" + window.FGS + "/api/addupage/";
        } else {
            formElem.action = "http://" + window.FGS + "/api/addpage/";
        }

        var url = document.createElement("input");
        url.type = "hidden";
        url.name = "url";
        url.value = window.FGURL || window.location;
        formElem.appendChild(url);

        var title = document.createElement("input");
        title.type = "hidden";
        title.name = "title";
        title.value = window.document.title;
        formElem.appendChild(title);

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
        alert(err.message);
    }
}

function tryAddPage() {
    var images = document.getElementsByTagName('img');
    var num_images = images.length;
    if (num_images == 0) {
        addpage();
        return;
    }
    
    var last_image = images[num_images - 1];
    if (last_image.complete) {
        addpage();
        return
    }
    
    last_image.onload = addpage;
    setTimeout(addpage, 3000);
}

if(window.FGQA && window.flowgram_quickadd_submitted) {
    alert("You already added this page :)");
} else {
	if(window.FGQA == 0) {
		window.location = "http://" + window.FGS + "/create/";
	} else if(window.FGB && window.FGF == undefined) {
        tryAddPage();
    }
}
