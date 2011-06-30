/**
 * @author Chris Yap
 * 	Flowgram Help Controller
 */

var HelpController = Class.create();

Object.extend(HelpController.prototype, {
	initialize: function(){
		
	},
	
	displayAnswer: function(answer_div_id) {
		
		new Effect.Fade($('main_help_index'), {duration: .2});
		new Effect.Appear($(answer_div_id), {duration: .3, queue: 'end'});
		
	},
	
	hideAnswer: function(answer_div_id) {
		new Effect.Fade($(answer_div_id), {duration: .2});
		new Effect.Appear($('main_help_index'), {duration: .3, queue: 'end'});
	}
	
	
});