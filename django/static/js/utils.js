/* Global JS utils */

function parseQueryParams() {
    var qsParam = new Array();

    var query = window.location.search.substring(1);
    var parms = query.split('&');
    for (var i=0; i < parms.length; i++) {
	    var pos = parms[i].indexOf('=');
	    if (pos > 0) {
		    var key = parms[i].substring(0,pos);
		    var val = parms[i].substring(pos+1);
    		
		    qsParam[key] = val;
	    }
    } 
    
    return qsParam;
}

var g_queryParams = parseQueryParams();

// This helps parse XML ajax responses
var XML = {};
XML.getRootNode = function(responseXML){ 
    switch(responseXML.childNodes.length){
        case 1: return responseXML.childNodes[0]; break;
        case 2: return responseXML.childNodes[1]; break;
        default: return false; break;
    }
};

// gets the total viewport height for most platforms and browsers
function getWindowHeight() {
	var windowHeight=0;
	if (typeof(window.innerHeight)=='number') {
		windowHeight=window.innerHeight;
	}
	else {
		if (document.documentElement && document.documentElement.clientHeight) {
			windowHeight=document.documentElement.clientHeight;
		}
		else {
			if (document.body && document.body.clientHeight) {
				windowHeight=document.body.clientHeight;
			}
		}
	}
	return windowHeight;
}

// get offset for top of viewport
function getScrollY() {
	var scrOfY = 0;
	if( typeof( window.pageYOffset ) == 'number' ) {
	    //Netscape compliant
	    scrOfY = window.pageYOffset;
	} else if( document.body && ( document.body.scrollLeft || document.body.scrollTop ) ) {
	    //DOM compliant
	    scrOfY = document.body.scrollTop;
	} else if( document.documentElement && ( document.documentElement.scrollLeft || document.documentElement.scrollTop ) ) {
	    //IE6 standards compliant mode
	    scrOfY = document.documentElement.scrollTop;
	}
	return scrOfY;
}

// javascript email validation
function echeck(str) {
		
	var at="@";
	var dot=".";
	var lat=str.indexOf(at);
	var lstr=str.length;
	var ldot=str.indexOf(dot);
	
	if ((str == null) || (str == '')) {
		return false
	}
	
	if (str.indexOf(at)==-1) {
	   return false
	}

	if (str.indexOf(at)==-1 || str.indexOf(at)==0 || str.indexOf(at)==lstr) {
	   return false
	}

	if (str.indexOf(dot)==-1 || str.indexOf(dot)==0 || str.indexOf(dot)==lstr) {
	    return false
	}

	 if (str.indexOf(at,(lat+1))!=-1) {
	    return false
	 }

	 if (str.substring(lat-1,lat)==dot || str.substring(lat+1,lat+2)==dot) {
	    return false
	 }

	 if (str.indexOf(dot,(lat+2))==-1) {
	    return false
	 }
	
	 if (str.indexOf(" ")!=-1) {
	    return false
	 }

	 return true					
}

// return domain
function getDomain() {
	var domain = window.location.href.split("/")[2];
	return domain;
}

// return fg flex URL
function getFGURL(path) {
	var domain = getDomain();
	url = 'http://' + domain + path;
	return url;
}

// check enter key for form submits
function checkEnter(e, form_element) {
	var characterCode = '';
	
	if(e && e.which) {
		e = e
		characterCode = e.which
	}
	
	else {
		e = event
		characterCode = e.keyCode
	}

	if(characterCode == 13 ){
		form_element.submit();
		return false
	}
	
	else{
		return true
	}

}

// check enter key for form submits - manual
function checkEnterManual(e) {
	var characterCode = '';
	
	if(e && e.which) {
		e = e
		characterCode = e.which
	}
	
	else {
		e = event
		characterCode = e.keyCode
	}

	if(characterCode == 13 ){
		return true
	}
	
	else{
		return false
	}

}

// validate email form
function validateEmailForm() {
	var form_element = $('email_form');
	var required_elements = form_element.select('[required="true"]');
	var error_text = '';
	var error_message = document.createElement('div');
	Element.addClassName(error_message, 'error');
	for (var i=0; i < required_elements.length; i++) {
		if (required_elements[i].value == '' || required_elements[i].value == null) {
			error_text += required_elements[i].name + ' is required.<br/>';	
		}
		if (required_elements[i].name == 'email') {
			var validemail = echeck(required_elements[i].value);
			if (validemail == false) {
				error_text += required_elements[i].name + ' is invalid.<br/>'
			}
		}
	}
	error_message.innerHTML = error_text;
	if (error_text != '') {
		Element.insert(form_element, {before:error_message});
		return false;
	}
	
	else {
		return true;
	}
}

function fgImgSwap(elemID, state) {
	if (state == 'over') {
		$(elemID).src = $(elemID).src.replace(/_off/, "_over");
	}
	else if (state == 'off') {
		$(elemID).src = $(elemID).src.replace(/_over/, "_off");
	}
}

function isValidEmail(email) {
	var regex = new RegExp("[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?");
    return regex.test(email);
}

// copy to clipboard
function copyToClipboard(inElement) {
  if (inElement.createTextRange && (sniff_br_id != 'msie')) {
    var range = inElement.createTextRange();
    if (range && BodyLoaded==1) {
      range.execCommand('Copy');
	}
  } 
  
  else {
    var flashcopier = 'flashcopier';
    if(!document.getElementById(flashcopier)) {
      var divholder = document.createElement('div');
      divholder.id = flashcopier;
      document.body.appendChild(divholder);
    }
    document.getElementById(flashcopier).innerHTML = '';
    var divinfo = '<embed src="/media/swf/clipboard/clipboard.swf" FlashVars="clipboard='+encodeURIComponent(inElement.value)+'" width="0" height="0" type="application/x-shockwave-flash"></embed>';
    document.getElementById(flashcopier).innerHTML = divinfo;
  }
}

// auto copy to clipboard
function autoCopyToClipboard(elementToCopy, statusElement) {
	elementToCopy.select();
	copyToClipboard(elementToCopy);
	var status = document.createElement('span');
	Element.addClassName(status, 'success');
	status.innerHTML = 'Copied';
	statusElement.appendChild(status);
	new Effect.Highlight(status,{duration:3, endcolor:'#E1F1F5'});
	new Effect.Fade(status,{duration:2, queue:'end'});
}

// clean email
function cleanEmails(emails) {
	emailPattern = /(?:"[^"]*"\s+)?<([^>]+)>/g;
	emails = emails.replace(emailPattern, '$1')
    return emails
}
