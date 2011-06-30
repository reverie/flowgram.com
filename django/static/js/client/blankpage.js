/**
 * @author Andrew Badr
 * 	Blank/Custom Page functionality
 */

var outerContainer = $('blank_page_editor');
var editor = $('editor');
var displayer = $('displayer');
var saveButton = $('saveButton');
var editButton = $('editButton');
var doneButton = $('doneButton');


function save() {
    saveButton.style.display = 'none';
	editButton.style.display = 'block';
	displayer.innerHTML = getHTML();
    editor.hide();
    $('editor_parent').hide();
    displayer.show();
}

function edit() {
    saveButton.style.display = 'block';
    editButton.style.display = 'none';
	displayer.hide();
    try {
        $('editor_parent').show();
    } catch(e) {}
}

function addFormInput(form, name, value) {
    var input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.value = value;
    form.appendChild(input);
}

function getHTML() {
    return '<table><tr><td>' + tinyMCE.get('editor').getDoc().body.innerHTML + '</td></tr></table>';
    //return '<html><head><style>body {background: white}</style></head><body>'+tinyMCE.get('editor').getContent()+'</body></html>';
}

function done() {
    // Create and post the form
    var f = document.createElement('form');
    f.method = "post";
    if (mode == 'new') {
        f.action = "/bp/create/";
        addFormInput(f, "fgid", fgid); // fgid variable is from outer HTML context
    } else {
        f.action = "/bp/save_edit/";
        addFormInput(f, "pid", pid); // fgid variable is from outer HTML context
    }
    addFormInput(f, "html", tinyMCE.get('editor').getDoc().body.innerHTML);
    addFormInput(f, "csrfmiddlewaretoken", csrfmiddlewaretoken); // fgid variable is from outer HTML context
    document.body.appendChild(f);
    f.submit();
}

function initTinyMCE() {
	tinyMCE.init({
	    mode : "exact",
	    elements: "editor",
	    theme: "advanced",
	    theme_advanced_toolbar_location : "top",
	    theme_advanced_toolbar_align : "left",
	    theme_advanced_buttons1 : "bold,italic,underline,strikethrough,separator," +
	                                  "justifyleft,justifycenter,justifyright,separator," +
	                                  "fontsizeselect,separator," +
	                                  "undo,redo,seperator,separator," +
	                                  "link,unlink",
	    theme_advanced_buttons2 : "bullist,numlist,separator,forecolor,backcolor",
	    theme_advanced_buttons3 : ""
	});

	edit();
}


