// REQUIRES window.fg_apr_id variable to be present (AddPageRequest id)

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
    return;
	var script_tags = doc.getElementsByTagName('script');
	//have to go backwards, because the array is dynamic..going forwards we'll only get every other one -andrew
	for(var i = script_tags.length - 2; i >= 0; i--) {
	    var script_tag = script_tags[i];
        if(script_tag.id != "fg_bookmarklet") {
            script_tag.parentNode.removeChild(script_tag);
        }
    }
}

KillJS(document);

function SetTitleToTitle() {
	document.title = window.document.title;
}

function SetURLToTitle() {
	document.title = window.location;
}

function SetAPRIDToTitle() {
	document.title = window.fg_apr_id;
}

function SetHTMLToTitle() {
	document.title = GetCurrentHTML();
}
