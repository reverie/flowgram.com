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

function getHTML(doc) {
    doctype = getDoctype(doc);
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
