/**
 * @author Chris Yap
 * 	Flowgram Admin Tools Controller
 */

var AdminToolsController = Class.create();

Object.extend(AdminToolsController.prototype, {
	initialize: function() { 
	
	},
	
	handleAdminNewestAjaxSubmit: function(fgid) {
		var currentInputID = 'displayInNewest_fgid_' + fgid;
		var currentInput = $(currentInputID);
		var token = $('csrf_token').innerHTML;
		var displayInNewest = '';
		
		if (currentInput.checked) {
			displayInNewest = 'True';
		}
		
		else {
			displayInNewest = 'False';
		}

        new Ajax.Request(
            '/api/admindisplayinnewest/',
            {
                parameters: {
                    flowgram_id: fgid,
					display_in_newest: displayInNewest, 
                    csrfmiddlewaretoken: token
                }
            });
	}
	
});
