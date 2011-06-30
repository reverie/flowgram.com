/**
 * @author Chris Yap
 * 	Flowgram Ajax Stat Record Controller
 */

var AjaxStatRecordController = Class.create();

Object.extend(AjaxStatRecordController.prototype, {
	initialize: function() { 
	
	},
	
	recordStat: function(label, num, string) {
		
		this.stat_label = label;
		this.stat_num = (num == null) ? 0 : num;
		this.stat_string = (string == null) ? '' : string;
		this.token = $('csrf_token').innerHTML;

        new Ajax.Request(
            '/api/recordstat/',
            {
				method: 'GET',
                parameters: {
                    type: this.stat_label,
					num: this.stat_num, 
                    string: this.stat_string,
					csrfmiddlewaretoken: this.token
                },
				onComplete: function()
				{
					//console.log('complete');
				}
            });
	}
	
});
